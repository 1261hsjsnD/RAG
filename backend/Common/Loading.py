#把所有要加载的都封装成一个类以免多次加载
import os
from dotenv import load_dotenv

from Common import Neo4j

# 先加载环境变量，保证模型路径 / API Key 可用
load_dotenv()

from ai import LLM, LoadEmbeddingModel, LoadRerankerModel, LoadChroma
from Chat.utils import BM25Util
from langchain_ollama import ChatOllama


class ModelLoader:
    """统一提前加载并持有所有模型对象的单例类，避免运行时多次加载。

    用法（只读方式）：
        from Common.Loading import loader
        loader.llm              # 回答模型（ChatOpenAI 客户端，全局复用同一实例）
        loader.embedding_model  # 向量化模型（HuggingFaceEmbeddings）
        loader.reranker         # 重排序模型（bge-reranker-large，仅加载一次）
        loader.chroma           # Chroma 向量库连接（law 集合）
        loader.bm25             # BM25 索引
        loader.bm25_docs        # BM25 对应的文档列表
        loader.ollama           # 本地 Ollama（qwen2.5，意图识别/对话摘要复用同一实例）
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all()
        return cls._instance

    def _load_all(self):
        print("[Loading] 开始预加载所有模型对象...")

        # 1. Embedding 向量化模型（模块级单例，import 时即已加载）
        self.embedding_model = LoadEmbeddingModel.embedding_model
        print("[Loading] Embedding 模型加载完成")

        # 2. 回答 LLM（远程 API 客户端，复用同一实例，避免每次请求新建）
        self.llm = LLM.load_model()
        print("[Loading] LLM 加载完成")

        # 3. 本地 Ollama（意图识别 / 对话摘要使用，复用同一实例）
        self.ollama = ChatOllama(
            model=os.getenv("OLLAMA_MODEL_NAME"),
            base_url=os.getenv("OLLAMA_BASE_URL"),
        )
        print("[Loading] Ollama 加载完成")

        # 4. 重排序模型（重量级本地模型，只加载一次）
        self.reranker = LoadRerankerModel.load_reranker_model()
        print("[Loading] Reranker 加载完成")

        # 5. Chroma 向量库连接（law 集合）
        self.chroma = LoadChroma.load_chrome_conn()
        print("[Loading] Chroma 加载完成")

        # 6. BM25 索引（命中磁盘缓存则秒级加载）
        self.bm25, self.bm25_docs = BM25Util.build_bm25_index(self.chroma)
        print("[Loading] BM25 索引加载完成")
        # 7. Neo4j 图数据库连接（复用同一实例，懒连接，不阻塞启动）
        self.neo4j = Neo4j.get_neo4j_conn()
        print("[Loading] Neo4j 连接加载完成")

        print("[Loading] 所有模型对象预加载完成")

    # ---- 以下方法与原有模块函数同名，方便后续其他文件切换引用 ----
    def load_model(self):
        return self.llm

    def load_reranker_model(self):
        return self.reranker

    def load_chrome_conn(self):
        return self.chroma

    def get_ollama(self):
        return self.ollama


# 模块导入时即创建实例，触发所有模型的提前加载
loader = ModelLoader()

if __name__ == '__main__':
    print("=" * 50)
    print("预加载验证结果：")
    print(f"  embedding_model : {type(loader.embedding_model).__name__}")
    print(f"  llm             : {type(loader.llm).__name__}")
    print(f"  reranker        : {type(loader.reranker).__name__}")
    print(f"  chroma          : {type(loader.chroma).__name__} / {loader.chroma._collection_name}")
    print(f"  bm25            : {type(loader.bm25).__name__} / docs={len(loader.bm25_docs)}")
    print(f"  ollama          : {type(loader.ollama).__name__} / {loader.ollama.model}")
    print("=" * 50)
