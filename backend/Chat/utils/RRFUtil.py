from langchain_core.documents import Document

def rrf(vector_result,bm25_result):
    """
        思路：
            循环比较vector_result和bm25_result的数据id
            id相同，就相加，id不同就独立存储


    """
    #score_dict:存储分数的字典
    score_dict ={}
    #docs_dict:存储文档的字典
    docs_dict={}
    #先处理向量检索的结果，把分值问题转换为排名问题
    for index,item in enumerate(vector_result,start=1):
        score_dict[item.id]=score_dict.get(item.id,0)+ round((1/(60+index)),4)
        docs_dict[item.id]=item
    #在处理BM25检索的结果，把分值问题转换为排名问题
    for index,item in enumerate(bm25_result,start=1):
        score_dict[item.id]=score_dict.get(item.id,0)+round((1/(60+index)),4)
        docs_dict[item.id]=item
    #rrf后排序
    sort_index=sorted(score_dict.items(),key=lambda x:x[1],reverse=True)
    #取出文档
    return [docs_dict[item[0]]for item in sort_index]