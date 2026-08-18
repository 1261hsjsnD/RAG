from langchain_chroma import Chroma
from ai import LoadEmbeddingModel
from dotenv import load_dotenv
load_dotenv()
import os
def load_chrome_conn():
    return Chroma(
        collection_name="law",
        persist_directory=os.getenv("CHROMA_PATH"),
        embedding_function=LoadEmbeddingModel.embedding_model
    )