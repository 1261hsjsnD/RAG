import json
from langchain_core.documents import Document
from langchain_chroma import Chroma
from ai import LoadEmbeddingModel
from pathlib import Path

current_path=Path(__file__).parent
DATA_PATH = current_path/"format_data.jsonl"
VECTOR_PATH = current_path.parent.parent / "Chroma"
COLLECTION_NAME = "medical"
BATCH_SIZE = 500
MIN_SCORE = None


def load_data():

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            question = d.get("question", "").strip()
            answer = d.get("answer", "").strip()
            if not question or not answer:
                continue
            if MIN_SCORE is not None and d.get("score", 0) < MIN_SCORE:
                continue
            content = f"问：{question}\n答：{answer}"
            metadata = {
                "label": d.get("label", ""),
                "source": DATA_PATH,
            }
            yield Document(page_content=content, metadata=metadata)


def main():
    chroma = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_PATH,
        embedding_function=LoadEmbeddingModel.embedding_model,
        collection_metadata={"hnsw:space": "cosine"},
    )
    count = 0
    batch = []
    for doc in load_data():
        batch.append(doc)
        if len(batch) >= BATCH_SIZE:
            chroma.add_documents(batch)
            count += len(batch)
            print(f"已写入 {count} 条")
            batch = []
    if batch:
        chroma.add_documents(batch)
        count += len(batch)
        print(f"已写入 {count} 条")
    print(f"全部完成，共 {count} 条")


if __name__ == "__main__":
    print(DATA_PATH )
