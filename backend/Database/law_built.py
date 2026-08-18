from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_chroma import Chroma
from ai import LoadEmbeddingModel
import pandas as pd
from pathlib import Path

current_path = Path(__file__).parent
file_path = current_path / "law_data" / "all_laws.txt"
loader = TextLoader(file_path,encoding="utf-8")
data = loader.load()
#向量数据库路径
vector_path = current_path / "Chroma"
#集合名
collection_name = "law"
#数据集路径
file_path = current_path / "law_data" / "all_laws.txt"
#读取数据
with open(file_path,"r",encoding="utf-8") as f:
    content =f.read()
data_list=[line.strip() for line in content.split("\n") if line.strip()]
#转换Document
documents=[
    Document(page_content=text,metadata={"source": file_path})
    for text in data_list
]
# 存入向量数据库
try:
    Chroma.from_documents(
        documents=documents,
        embedding=LoadEmbeddingModel.embedding_model,
        persist_directory=vector_path,
        collection_name=collection_name,
        collection_metadata={"hnsw:space": "cosine"},
    )
    print(f"数据存入成功，共 {len(documents)} 条")
except Exception as e:
    print(f"数据存入失败:{e}")
