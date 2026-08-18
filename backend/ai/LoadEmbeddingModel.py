from langchain_huggingface import HuggingFaceEmbeddings
embedding_model=HuggingFaceEmbeddings(
    model_name=r"E:\Models\paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={
        "device": "cuda",
        "local_files_only": True,
    },
)