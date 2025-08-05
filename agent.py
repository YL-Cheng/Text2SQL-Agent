import re
import yaml
import logging
from typing import Union
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, AgentExecutor
from langchain.utilities import SQLDatabase
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import ListSQLDatabaseTool, InfoSQLDatabaseTool

from src.database import create_sql_engine
from src.schema import create_schema
from src.llm import init_llm_local, init_llm_gemini
from src.retriever import init_retriever

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')


def build_list_table_tool(db: SQLDatabase) -> Tool:
    """
    Builds and returns a LangChain Tool for listing all available table names in the database.

    This tool uses the `ListSQLDatabaseTool` to discover which tables are present
    in the connected SQL database.

    Args:
        db (SQLDatabase): The SQLDatabase wrapper instance.

    Returns:
        Tool: A LangChain Tool configured to list database table names.
    """
    list_tables = ListSQLDatabaseTool(db=db)
    return Tool(
        name="list_tables",
        func=list_tables,
        description="Use this tool to list all available table names in the database."
    )

def build_info_table_tool(db: SQLDatabase) -> Tool:
    """
    Builds and returns a LangChain Tool for describing the schema of a specific table.

    This tool uses the `InfoSQLDatabaseTool` to provide detailed information about
    a given table, including its column names and data types.

    Args:
        db (SQLDatabase): The SQLDatabase wrapper instance.
    Returns:
        Tool: A LangChain Tool configured to describe a specific database table.
    """
    describe_table = InfoSQLDatabaseTool(db=db)
    return Tool(
        name="describe_table",
        func=lambda table: describe_table.invoke(input=table),
        description="Use this tool to describe the schema of a specific table, including column names and data types."
    )

def build_schema_tool(retriever: VectorStoreRetriever) -> Tool:
    """
    Return a Tool for schema lookup using the retriever.

    This tool allows the agent to query the database schema for definitions
    and descriptions of tables and columns.

    Args:
        retriever (VectorStoreRetriever): The retriever instance (e.g., Chroma retriever) used to search schema documents.

    Returns:
        Tool: A LangChain Tool configured for schema lookup.
    """
    return Tool(
        name="schema_lookup",
        func=lambda query: retriever.get_relevant_documents(query),
        description=(
            "A tool to retrieve definitions of table or column names. "
            "Use when the input is a natural language question containing a field or table name that needs clarification."
            "Input should be a short query or phrase asking about the meaning or definition of a table or column. "
            "Returns the associated schema documentation."
        )
    )

def build_sql_generation_tool(llm: Union[LlamaCpp, ChatGoogleGenerativeAI], 
                              db: SQLDatabase, 
                              chain_template_path: str = "template/sql_db_chain_v1.1.yml", 
                              max_retries: int = 3,
                              verbose: bool = False) -> Tool:
    """
    Return a Tool for SQL queries using SQLDatabaseChain with prompt loaded from external file.

    Args:
        llm (LlamaCpp, ChatGoogleGenerativeAI): The language model to use.
        db (SQLDatabase): The SQLDatabase wrapper instance.
        chain_template_path (str): Path to the prompt template file. Defaults to "template/sql_db_chain_v1.1.yml".
        max_retries (int): The maximum number of retries for SQL query execution. Defaults to 3.
        verbose (bool): Whether to print verbose output. Defaults to False.

    Returns:
        Tool: A LangChain Tool configured for executing SQL queries.
    """
    with open(chain_template_path, "r") as f:
        chain_template_dict = yaml.safe_load(f)

    chain_prompt = PromptTemplate(
        input_variables=["input", "table_info", "dialect"],
        template=chain_template_dict['instruction'],
    )

    sql_generation_chain = LLMChain(llm=llm, prompt=chain_prompt, verbose=verbose)

    def safe_sql_query(question, max_retries=max_retries):
        """
        Executes a query with a retry-and-correct mechanism.
        """
        
        table_info = db.get_table_info()
        dialect = db.dialect
        
        chain_input = {
            "input": question,
            "table_info": table_info,
            "dialect": dialect
        }
        
        for i in range(max_retries):
            logging.info(f"Attempt {i + 1} of {max_retries} in query db data")
            sql_code = sql_generation_chain.invoke(chain_input)['text']

            match = re.search(r"SQLQuery:\s*(.*?)(?=\nSQLResult:)", sql_code, re.DOTALL)
            if match:
                sql_code = match.group(1)
            sql_code = sql_code.strip().replace("```sql", "").replace("```", "").strip()
            
            try:
                logging.info(f"Executing SQL: {sql_code}")
                result = db.run(sql_code)
                logging.debug("Query Successful!")
                return f"Query executed successfully. Result: {result}"
            except Exception as e:
                error_message = str(e)
                logging.debug(f"Query Failed. Error: {error_message}")
                
                if i == max_retries - 1:
                    return f"Failed to execute SQL after {max_retries} attempts. Last error: {error_message}"
                
                chain_input["input"] = (
                    f"The previous attempt to answer the question '{question}' failed. "
                    f"The generated SQL was:\n{sql_code}\n"
                    f"It produced the following database error:\n{error_message}\n"
                    "Please analyze the error and the database schema to generate a corrected SQL query."
                )

        return "Failed to get a valid response from the database after multiple attempts."

    return Tool(
        name="sql_query",
        func=safe_sql_query,
        description=(
            "Use this tool to answer questions about user data, metrics, or reports from the database. "
            "Input should be a complete question in natural language. "
            "The tool will automatically generate, execute, and correct SQL to find the answer."
        )
    )

def build_agent(llm: Union[LlamaCpp, ChatGoogleGenerativeAI], 
                db: SQLDatabase, 
                retriever: VectorStoreRetriever, 
                agent_template_path: str = "template/sql_agent_v1.1.yml",
                verbose: bool = False):
    """
    Builds and returns a LangChain agent capable of answering questions
    by interacting with a SQL database and its schema.

    The agent is initialized with four tools:
    `list_tables`, `describe_table`, `sql_query`, and `schema_lookup`.

    Args:
        llm (LlamaCpp, ChatGoogleGenerativeAI): : The language model to use.
        db (SQLDatabase): The SQLDatabase wrapper instance.
        retriever (VectorStoreRetriever): The retriever instance for schema lookup.
        agent_template_path (str): Path to the agent prompt template file. Defaults to "template/sql_agent_v1.1.yml".
        verbose (bool): Whether to print verbose output. Defaults to False.
    
    Returns:
        langchain.agents.agent.AgentExecutor: An initialized LangChain agent.
    """
    with open(agent_template_path, "r", encoding="utf-8") as f:
        agent_template_dict = yaml.safe_load(f)
    
    # Create agent
    list_table_tool = build_list_table_tool(db)
    info_table_tool = build_info_table_tool(db)
    sql_generation_tool = build_sql_generation_tool(llm, db, verbose=verbose)
    schema_tool = build_schema_tool(retriever)
    tools = [list_table_tool, info_table_tool, sql_generation_tool, schema_tool]

    ## custom agent
    agent_prompt = ZeroShotAgent.create_prompt(
        tools=tools,
        prefix=agent_template_dict['prefix'],
        suffix=agent_template_dict['suffix'],
        format_instructions=agent_template_dict['instruction'].replace("{table_list}", str(list_table_tool.invoke(""))),
        input_variables=["input", "agent_scratchpad"],
    )

    agent = ZeroShotAgent(
        llm_chain=LLMChain(llm=llm, prompt=agent_prompt),
        allowed_tools=[t.name for t in tools],
        stop=["\nFinal Answer:"],
    )

    executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        # max_iterations=3,
        early_stopping_method="generate",
        handle_parsing_errors=True,
        verbose=verbose,
    )

    return executor


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", type=str, required=True, help="Query to be executed.")
    parser.add_argument("-k", "--key",   type=str, required=True, help="API key for Google Generative AI.")
    options = parser.parse_args()

    # Initialize SQLite DB
    engine, _ = create_sql_engine()
    db = SQLDatabase(engine, include_tables=["members", "items", "campaigns", "transactions", "transaction_items"])

    # Initialize schema retriever and tools
    llm = init_llm_gemini(api_key=options.key)
    df_schema = create_schema()
    retriever = init_retriever(df_schema)
    
    # Build agent
    agent = build_agent(llm, db, retriever)
    logging.info("Agent initialized. Ready to run queries.")
    print(agent.invoke(options.query))