# Text2SQL-Agent: A Natural Language to SQL Agent

A powerful tool that converts natural language questions into SQL queries and executes them on a database to return accurate answers. This project leverages Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to understand database schemas, generate executable SQL, and provide immediate, meaningful insights from the data.


## How It Works
The workflow is as follows:

1.  **Initialization:**
    On startup, the application uses SQLAlchemy to create a simulated in-memory SQLite database and populates it with synthetic e-commerce data using the Faker package.

2.  **Schema Retriever Creation:**
    The database schema defined in `src/schema.py` is loaded, then converted into vector embeddings using `sentence-transformers`, and stored in a ChromaDB vector database.

3.  **Agent and Tools:**
    A conversational agent is built using LangChain. It is equipped with a set of tools to interact with the database:
    - `list_tables`: Lists all available tables.
    - `describe_table`: Shows the schema for a specific table.
    - `schema_lookup`: Retrieves detailed definitions for tables or columns (using RAG).
    - `sql_query`: Generates, executes, and automatically corrects SQL queries.

4.  **Reasoning and Execution:**
    When a user asks a question (e.g., "Who are the top five members with the highest sales?"), the agent follows a reasoning process (ReAct) to decide which tools to use. It might first inspect the tables, then look up column definitions, and finally use the `sql_query` tool to generate and run the final SQL.

5.  **Response Generation:**
    The agent executes the generated SQL query against the database and returns the results in a formatted response.


## Installation and Setup
1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-username/Text2SQL-Agent.git
    cd Text2SQL-Agent
    ```

2.  **Install dependencies**
    Creating a virtual environment before installing the packages is recommended.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up environment variables**
    - **To use Gemini:**
      You will need a Google API key. How you provide it depends on how you run the agent:
      - **For the Jupyter Notebook (`run_agent.ipynb`):** The notebook reads the API key from an environment variable named `GOOGLE_API_KEY`. Before launching Jupyter, you must set this variable in your terminal:
        ```bash
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        ```
      - **For the Command-Line (`agent.py`):** The script expects the API key to be passed as an argument. See the Usage section below.

    - **To use a local model:**
      Download a GGUF-formatted local model (e.g., Gemma) and place it in the `models/` directory.


## Usage
There are two primary ways to use this agent:

### 1. Jupyter Notebook (Recommended)
The `run_agent.ipynb` notebook provides an interactive environment for testing the agent. It walks through the setup and includes several example queries in both English and Chinese.

1.  Set your `GOOGLE_API_KEY` environment variable as described in the Setup section.
2.  Launch Jupyter and open `run_agent.ipynb`.
3.  Run the cells sequentially to see the agent in action.

### 2. Command-Line Interface
You can also run the agent directly from the command line using `agent.py`. This method requires passing your Google API key using the `-k` flag.

```bash
python agent.py -q "How many transactions were made using LinePay?"
```

## Project Structure
```
Text2SQL-Agent/
├── models/
│   └── *.gguf            # Stores local GGUF models
├── src/
│   ├── database.py       # Defines database schema and generates synthetic data
│   ├── schema.py         # Defines the database schema and its descriptions
│   ├── llm.py            # Initializes LLMs (Gemini or local models)
│   ├── retriever.py      # Builds a RAG retriever for database schema
│   └── __init__.py
├── template/
│   ├── sql_agent_v*.yml
│   └── sql_db_chain_v*.yml
├── .env                  # (Optional) Stores environment variables
├── README.md             # This documentation file
└── requirements.txt      # Project dependencies
```