import logging
import pandas as pd
from langchain.schema import Document
from langchain.vectorstores import Chroma
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.base import VectorStoreRetriever

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')


def init_retriever(df_schema: pd.DataFrame, embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> VectorStoreRetriever:
    """
    Create and return a Chroma retriever for schema documents.

    Args:
        df_schema (pd.DataFrame): A DataFrame containing the database schema definition,
                                  expected to have columns like 'table_name', 'column_name',
                                  'data_type', 'column_name_zh', and 'definition'.
        embedding_model_name (str): The name of the HuggingFace embedding model to use.
                                    Defaults to "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2".

    Returns:
        langchain.vectorstores.Chroma.as_retriever: A retriever configured for schema lookup.
    """
    logging.info(f"Initializing Chroma retriever with embedding model: {embedding_model_name}")
    docs = []
    for table_name, columns in df_schema.groupby("table_name"):
        content = (
            f"{table_name}: {', '.join(columns)}"
        )
        docs.append(Document(page_content=content, metadata={"table_name": table_name}))
    for _, row in df_schema.iterrows():
        content = (
            f"{row['table_name']}.{row['column_name']}: "
            f"[{row['data_type']}] {row['definition']}"
        )
        docs.append(Document(page_content=content, metadata=row.to_dict()))
    embedding = HuggingFaceEmbeddings(model_name=embedding_model_name)
    vecdb = Chroma.from_documents(docs, embedding)
    return vecdb.as_retriever(search_type="mmr", search_kwargs={"k": 3})