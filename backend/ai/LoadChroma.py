from langchain_chroma import Chroma
from ai import LoadEmbeddingModel
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
def load_chrome_conn():
    return Chroma(
        collection_name="law",
        persist_directory=str(Path(__file__).parents[1] / "Database" / "Chroma"),
        embedding_function=LoadEmbeddingModel.embedding_model
    )