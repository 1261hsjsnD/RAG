from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from ai import LoadChroma
import jieba
import pickle
import os

# 中文常用停用词表
STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
    "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
    "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它", "们",
    "这个", "那个", "什么", "哪", "怎么", "吗", "呢", "吧", "啊", "哦",
    "还", "被", "把", "让", "从", "对", "与", "但", "而", "或", "所",
    "为", "以", "及", "可", "可以", "能", "能够", "应该", "需要", "已经",
    "虽然", "如果", "因为", "所以", "只是", "还是", "不过", "然后",
    "之", "其", "中", "等", "等等", "即", "使", "向", "将", "按", "当",
    "于", "由", "比", "除了", "关于", "以及", "并且", "此外", "另外",
    "过", "着", "来", "去", "做", "作", "像", "如", "如同", "由于",
])

# BM25索引缓存：key为集合名
_bm25_cache = {}

# BM25索引磁盘持久化目录
_BM25_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Database", "Chroma", "bm25_cache",
)


# 分词
def tokenize(text):
    results = jieba.cut(text)
    return [item for item in results if item.strip() not in STOP_WORDS]


def _cache_path(key):
    safe_key = "".join(c if c.isalnum() else "_" for c in key)
    return os.path.join(_BM25_CACHE_DIR, f"bm25_{safe_key}.pkl")


def build_bm25_index(vector_db):
    key = getattr(vector_db, "_collection_name", "") or str(id(vector_db))

    # 查内存
    if key in _bm25_cache:
        print(f"[BM25] 命中内存缓存：{key}")
        return _bm25_cache[key]

    # 查磁盘 命中回填内存
    path = _cache_path(key)
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                result = pickle.load(f)
            _bm25_cache[key] = result
            print(f"[BM25] 命中磁盘缓存：{path}")
            return result
        except Exception as e:
            print(f"[BM25] 磁盘缓存加载失败（{e}），重新构建")

    # 重新构建
    print(f"[BM25] 开始构建 {key} 索引...")
    raw = vector_db.get()
    ids = raw['ids']
    documents = raw['documents']
    metadatas = raw['metadatas']

    doc_list = [
        Document(id=ids[i], page_content=documents[i],
                 metadata={"source": metadatas[i]})
        for i in range(len(ids))
    ]
    corpus = [tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(corpus)
    result = (bm25, doc_list)

    # 回填内存 + 写入磁盘
    _bm25_cache[key] = result
    os.makedirs(_BM25_CACHE_DIR, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(result, f)
    print(f"[BM25] 构建完成，已持久化到 {path}")
    return result


# BM25检索
def bm25_search(bm25, question, docs, k=10):
    scores = bm25.get_scores(tokenize(question))
    sort_scores_index = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [docs[i] for i in sort_scores_index]


if __name__ == '__main__':
    vector_db = LoadChroma.load_chrome_conn()
    bm25, docs = build_bm25_index(vector_db)
    result = bm25_search(bm25, "在医院打人了怎么办", docs)
    print(result)