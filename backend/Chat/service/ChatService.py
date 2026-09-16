from Common.Tools import retrieve,get_weather,query_neo4j
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AIMessageChunk
from langchain.agents import create_agent
from Common.Loading import loader
from Chat.dao import MenuDao
def chat(question,historyId,email):
    history_message = []
    if historyId != 0:
        summaries = MenuDao.summary_history(historyId, email)
        recent = MenuDao.history_dao2(historyId, email)["data"]
        history_message = []
        for i in summaries:
            history_message.append(SystemMessage(content=f"历史对话摘要:{i["compress"]}"))
        for item in recent:
            if item.get("role") == "user":
                history_message.append(HumanMessage(content=item["content"]))
            elif item.get("role") == "assistant":
                history_message.append(AIMessage(content=item["content"]))
    agent = create_agent(
        # llm
        model=loader.llm,
        # 系统提示词：告诉agent如何工作
        system_prompt="""
          你是一个智能助手，请严格遵循以下规则响应用户请求：

           ## 工具调用规则
           1. **天气查询**：当用户询问天气、气温、湿度、风力等气象信息时，必须调用 `get_weather` 工具获取实时数据，禁止凭记忆回答。
           2. **法律知识查询**：当用户询问法律法规、司法解释、合同条款、法律程序等纯法律问题时，必须调用 `retrieve` 工具（related="law"）从法律条文库检索原文，禁止凭记忆回答或自行解读。
           3. **医疗健康查询**：当用户咨询疾病、症状、用药、诊疗建议、医学概念等健康问题时，必须按顺序连续调用两个工具：
           - 第一步：调用 `retrieve`（related="medical"）从医患问答库获取参考性问答；
           - 第二步：调用 `query_neo4j` 从医学知识图谱获取实体关系、病理机制、药物相互作用等结构化知识。
            两步均完成后，方可整合结果回复。禁止仅调用其中一个工具，禁止调换调用顺序。
           4. **其他问题**：若用户问题不涉及上述三类场景，直接基于自身知识生成准确、简洁的回复，无需调用任何工具。

           ## 重要约束
           - 医疗场景必须完成 retrieve(medical) + query_neo4j 两次调用，缺一不可；天气和法律场景仅调用对应单个工具。
           - 每次响应中工具调用总数不超过2次，且仅在医疗场景下允许达到2次。
           - 禁止在医疗场景中调用 retrieve(law)，禁止在法律场景中调用 retrieve(medical) 或 query_neo4j。各知识库内容完全隔离，无交叉数据。
           - 工具返回结果后，需结合原始问题进行自然语言整合，不得直接输出原始文本片段或图数据库原始三元组。
           - 回复医疗内容时，必须包含免责声明："以下为参考性信息，不构成诊疗建议，具体请遵医嘱。"
           - 引用法律条文时应忠实原文，禁止概括改写导致语义偏差；禁止编造法条编号、药品批准号等出处标识。
           - 若任一工具调用失败或无匹配结果，如实告知用户缺失部分的信息，并给出替代建议（如调整提问方式、咨询专业机构），不得虚构内容填补空白。
               """,
        # 工具列表
        tools=[get_weather, query_neo4j, retrieve],
    )

    # stream_mode="messages"：产出 (AIMessageChunk, metadata) 元组，每个 chunk 是真正的 token 增量
    for msg_chunk, _metadata in agent.stream(
            {"messages": history_message + [HumanMessage(content=question)]},
            stream_mode="messages",
    ):
        # 只输出模型最终回答的文本增量；工具调用参数/工具结果会自动被过滤（content 为空或非 AIMessageChunk）
        if isinstance(msg_chunk, AIMessageChunk) and msg_chunk.content:
            yield msg_chunk.content

if __name__ == '__main__':
    question="我发烧了怎么办"
    historyId=1
    for chunk in chat(question,historyId):
        if chunk:
            print(chunk)
