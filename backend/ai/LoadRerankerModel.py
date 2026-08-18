from FlagEmbedding import FlagReranker

def load_reranker_model():
    return FlagReranker(
        model_name_or_path="E:\\Models\\bge-reranker-large_v1",
        use_fp16=True,
    )