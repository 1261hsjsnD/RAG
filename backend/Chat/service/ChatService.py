from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from ai import LLM,LoadEmbeddingModel,LoadRerankerModel
from langchain_chroma import Chroma
from Chat.utils import BM25Util, RRFUtil, IntentionUtil
from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableLambda
from Chat.dao import MenuDao
from pathlib import Path
def chat(question,historyId):
    if historyId==0:
        history=[]
    else:
        history = MenuDao.history_dao(historyId)["data"]
    ollamallm=IntentionUtil.intention_recogntion(question)

    print(ollamallm)
    # 加载回答模型
    llm = LLM.load_model()
    if ollamallm :
        related=ollamallm["related"]

        #提示词
        Prompt="""
                你是一个基于知识库的AI助手。请严格根据参考资料回答用户问题。

                【回答规则】
                1. 仅使用参考资料中的信息作答，禁止使用任何外部知识或自行补充建议。
                2. 参考资料充足时：直接提炼关键答案，语言自然简洁，不要冗长解释。
                3. 参考资料不足或无关时：仅回复"当前知识库中暂未找到相关信息，建议您换个方式描述问题，或咨询相关专业人士。"，不要猜测，不要给出任何建议或替代方案。
                4. 涉及法律问题时：在回答末尾另起一行添加"⚖️ 以上内容仅供参考，不构成法律意见，具体请咨询专业律师。"
                5. 涉及医疗/健康问题时：在回答末尾另起一行添加"🏥 以上内容仅供参考，不构成医疗建议或诊断，如有不适请及时就医。"
                6. 若同一问题同时涉及法律和医疗，则两条声明均需添加。
                
                【禁止事项】
                - 禁止提及"参考资料""检索内容""知识库""提供的信息"等字眼，不要描述你的检索过程或资料内容。
                - 禁止输出"根据……""基于……""资料显示……"等引导语。
                - 禁止在信息不足时自行补充建议、方案或引导用户采取其他行动。
                - 禁止修改、省略或改写上述法律和医疗免责声明的措辞，必须原文完整输出。
                - 禁止在非法律/非医疗类回答中添加任何免责声明。
                
                【历史记录】
                {history}
                
                【参考资料】
                {context}
                
                【用户问题】
                {question}
                
                【回答】
            """
        #创建提示词对象
        prompt=PromptTemplate(
            template=Prompt,
            input_variables=["history","context","question"]
        )
        #创建检索器对象
        vector_db=Chroma(
            collection_name=related,
            persist_directory=str(Path(__file__).parents[2] / "Database" / "Chroma"),
            embedding_function=LoadEmbeddingModel.embedding_model,

        )

        vector_retriever=vector_db.as_retriever(search_kwargs={"k":10})
        # 打印召回结果
        def print_recall(title, docs):
            print(f"{title}到的文档内容")
            for doc in docs:
                print(doc.page_content)
            return docs
        def retriever_func(question):
            #向量检索
            vector_result =vector_retriever.invoke(question)
            print_recall("向量检索", vector_result)
            #BM25检索
            bm25,docs=BM25Util.build_bm25_index(vector_db)
            bm25_result=BM25Util.bm25_search(bm25,question,docs,10)
            print_recall("BM25检索",bm25_result)
            #rrf融合
            rrf_result=RRFUtil.rrf(vector_result,bm25_result)
            print_recall("RRF融合",rrf_result)
            return rrf_result

        #加载重排序模型
        reranker=LoadRerankerModel.load_reranker_model()
        def reranker_func(data):
            print("开始重排序")
            history=data['history']
            docs=data['context']
            question=data['question']
            queire=[(question,doc.page_content) for doc in docs]

            scores=reranker.compute_score(queire)
            results=list(zip(docs,scores))
            #降序
            results.sort(key=lambda x:x[1],reverse=True)
            docs_3=[doc.page_content for doc,score in results[:3]]
            context="\n\n".join(f"来源{i+1}:{text}"for i,text in enumerate(docs_3))
            print(f"重排序后：{context}")
            return{
               'history':history,
                'context':context,
                'question':question,
            }
        #构造链
        qa_chain=(
            RunnableParallel({
                "history": RunnableLambda(lambda _:history),
                "context": RunnableLambda(lambda _:retriever_func(question)),
                "question":RunnablePassthrough(),

            }


            )
            | RunnableLambda(reranker_func)
            | prompt
            | llm
            |StrOutputParser()

        )

        for chunk in qa_chain.stream(question):
            if hasattr(chunk,'content'):
                yield chunk.content
            else:
                yield chunk
    else:
        history.append(question)
        for chunk in llm.stream(history):
            if chunk.content:
                yield chunk.content
        return

if __name__ == '__main__':
    question="我发烧了怎么办"
    historyId=1
    for chunk in chat(question,historyId):
        if chunk:
            print(chunk)
