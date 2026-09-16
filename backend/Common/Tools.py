import os
import json
from langchain.agents import create_agent

import requests
from langchain_core.tools import tool
from Common.Loading import loader
from pydantic import BaseModel, Field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from Common.Loading import loader
from langchain_chroma import Chroma
from Chat.utils import BM25Util, RRFUtil, IntentionUtil
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from Chat.dao import MenuDao
from pathlib import Path

# 获取neo4j连接
graph = loader.neo4j


class WeatherTool(BaseModel):
    city: str = Field(..., description="城市名")


class Neo4jEntity(BaseModel):
    cql: str = Field(..., title="查询命令")


class RetrivalTool(BaseModel):
    question: str = Field(..., title="用户问题")
    related: str = Field(..., title="数据库名称")


# 天气查询工具
@tool(
    name_or_callable="get_weather",
    description="""
    获取指定城市当前及未来3天的天气预报信息。

    【触发条件】
    当用户的意图涉及以下任一场景时调用此工具：
    - 明确询问某城市的天气、气温、降水、风力等气象信息
    - 询问出行建议、穿衣建议、是否带伞等与天气强相关的问题
    - 对比多个城市的天气状况

    【不应调用】
    - 查询历史天气数据（本工具仅支持当前+未来3天）
    - 查询空气质量/AQI、紫外线指数等非基础气象指标
    - 用户未提及任何地理位置且上下文中也无法推断出城市

    【参数】
    - city (str, 必填): 城市名称。
      · 优先使用中文标准城市名（如"北京"而非"Beijing""北京市"）
      · 若用户使用英文/拼音，需先转换为中文再传入
      · 不支持区县级别（如"朝阳区"），请提取所属城市
      · 若用户未指定城市但上下文中有明确位置信息，自动提取并传入
      · 若完全无法确定城市，不要调用此工具，应先反问用户


    失败时返回：{"error": "未找到城市'xxx'的天气数据，请确认城市名称"}

    【注意事项】
    - 温度单位为摄氏度(°C)，降水概率为百分比
    - 数据更新频率为每小时，非实时秒级
    - 回答用户时应基于返回的 forecast 数据给出具体建议，不要凭常识推测
    """,
    args_schema=WeatherTool,

)
def get_weather(city: str) -> dict:
    print(f"查询{city}的天气")
    # 高德查询接口
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": os.getenv("GAODE_API_KEY"),
        "city": city,
    }
    # 通过requersts发送get请求
    rs = requests.get(url, params=params)
    result = rs.json()
    # 高德接口失败时（如 key 未配置/无效）友好返回，不中断 agent 流程
    if result.get("status") != "1":
        return {"result": f"天气查询失败：{result.get('info', '未知错误')}（请检查 GAODE_API_KEY 是否配置正确）"}
    # 拼接天气数据
    live = result["lives"][0]
    return {
        "result": (
            f"{live['province']}{live['city']}当前天气{live['weather']}，"
            f"气温{live['temperature_float']}℃，湿度{live['humidity_float']}%，"
            f"{live['winddirection']}风{live['windpower']}级，"
            f"数据更新时间为{live['reporttime']}。"
        )
    }


# 查图数据库
@tool(
    name_or_callable="query_neo4j",
    description="""
        Task:Generate Cypher statement to query a graph database.
        Instructions:
        Use only the provided relationship types and properties in the schema.
        Do not use any other relationship types or properties that are not provided.
        数据库的信息定义如下：
        # 节点标签及含义
        | 节点标签     | 含义             |
        |--------------|------------------|
        | Disease      | 疾病（核心节点） |
        | Symptom      | 症状             |
        | Check        | 检查项目         |
        | Cureway      | 治疗方式         |
        | Drug         | 药物             |
        | Department   | 就诊科室         |
        | Food         | 食物             |
        | Dishes       | 菜肴             |
        | Category     | 疾病分类         |

        # 关系类型及含义
        | 关系类型             | 含义              | 起始节点 | 目标节点    |
        |----------------------|-------------------|----------|-------------|
        | DISEASE_SYMPTOM      | 疾病症状          | Disease  | Symptom     |
        | DISEASE_CHECK        | 相关检查项目      | Disease  | Check       |
        | DISEASE_CUREWAY      | 治疗方式          | Disease  | Cureway     |
        | DISEASE_DRUG         | 治疗或相关药物    | Disease  | Drug        |
        | DISEASE_DEPARTMENT   | 就诊科室          | Disease  | Department  |
        | DISEASE_DO_EAT       | 推荐进食的食物    | Disease  | Food        |
        | DISEASE_NOT_EAT      | 不推荐进食的食物  | Disease  | Food        |
        | DISEASE_DISHES       | 适合疾病的菜肴    | Disease  | Dishes      |
        | DISEASE_ACOMPANY     | 并发症 / 伴随疾病 | Disease  | Disease     |
        | DISEASE_CATEGORY     | 疾病所属类别      | Disease  | Category    |

        # 查询示例（注意：Cypher 属性用单花括号，如 {name:"高血压"}）
        # 问：高血压有哪些症状？
        MATCH (d:Disease {name:"高血压"})-[:DISEASE_SYMPTOM]->(s:Symptom) RETURN s.name AS symptom

        # 问：感冒吃什么药？
        MATCH (d:Disease {name:"感冒"})-[:DISEASE_DRUG]->(dr:Drug) RETURN dr.name AS drug

        # 问：糖尿病不宜吃什么？
        MATCH (d:Disease {name:"糖尿病"})-[:DISEASE_NOT_EAT]->(f:Food) RETURN f.name AS food

        # 问：肺炎需要做什么检查？
        MATCH (d:Disease {name:"肺炎"})-[:DISEASE_CHECK]->(c:Check) RETURN c.name AS check_item

        # 问：高血压挂什么科？
        MATCH (d:Disease {name:"高血压"})-[:DISEASE_DEPARTMENT]->(dep:Department) RETURN dep.name AS department

        # 问：感冒的并发症有哪些？
        MATCH (d:Disease {name:"感冒"})-[:DISEASE_ACOMPANY]->(a:Disease) RETURN a.name AS complication

        # 问：糖尿病属于哪类疾病？
        MATCH (d:Disease {name:"糖尿病"})-[:DISEASE_CATEGORY]->(c:Category) RETURN c.name AS category

        # 问：高血压可以吃什么菜？
        MATCH (d:Disease {name:"高血压"})-[:DISEASE_DISHES]->(dishes:Dishes) RETURN dishes.name AS dishes

        # 问：哪些疾病会有头痛症状？
        MATCH (d:Disease)-[:DISEASE_SYMPTOM]->(s:Symptom {name:"头痛"}) RETURN d.name AS disease

        Note: Do not include any explanations or apologies in your responses.
        Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
        Do not include any text except the generated Cypher statement.

        参数：
            cql: 查询命令
    """,
    args_schema=Neo4jEntity
)
def query_neo4j(cql: str) -> dict:
    result = graph.query(cql)
    return {
        "result": result
    }


@tool(
    name_or_callable="retrieve",
    description="""
    在专业知识库中进行语义向量检索，根据用户问题类型选择对应知识集合获取权威依据。

    【触发条件】
    当用户的意图涉及以下任一场景时调用此工具：
    - 询问具体法律条文、法规原文、司法解释文本 → 使用 related=law（内容为纯法条原文）
    - 咨询疾病症状、用药疑问、诊疗建议等患者视角的健康问题 → 使用 related=medical（内容为医患问答对）
    - 医疗纠纷、职业病认定等交叉问题 → 先用 related=law 查法律依据，再用 related=medical 查医学事实

    【不应调用】
    - 纯日常闲聊、非法律/医疗领域的通用知识问答
    - 要求提供确定性诉讼胜负预测或个性化诊疗处方
    - 查询律师/医生联系方式、案件进度、挂号信息等非知识库内容
    - 用户问题无法归类到法条检索或健康问答任一场景

    【参数】
     - question (str, 必填): 向知识库提出的问题。
      · law 集合：使用规范法律表述，可直接包含条款号、法规名称
        示例："劳动合同法第四十七条经济补偿标准" "民法典医疗损害责任条款"
      · medical 集合：使用患者自然语言提问，贴近真实问诊口吻，不要改写为专业术语
        示例："孩子发烧39度吃了布洛芬不退烧怎么办" "长期失眠应该挂什么科"
      · 若无法判断问题类型，应先追问澄清，不要猜测集合
      · 单次不超过100字，复杂问题拆分为多次调用
    - related (str, 必填): 知识集合标识。
      · 可选值: "law" | "medical"
      · law = 纯法律条文原文集合；medical = 医患问答对集合
      · 严格根据问题类型选择，禁止传入其他值
      · 交叉问题优先 "law"，补充医学事实时再调 "medical"

    失败时返回：{"error": "未在'{related}'集合中检索到与'xxx'相关的内容，请尝试调整查询表述或确认问题类型"}

    【注意事项】
    - 系统自动精排并固定返回最相关的3条内容，无法指定数量
    - 返回结果为纯文本片段列表，无标题、来源ID、日期等元数据
    - law 返回的是法条原文片段，回答时应忠实引用原文，禁止概括改写导致语义偏差
    - medical 返回的是医生对特定患者的回复，具有个体化语境，回答时必须声明"以下为参考性医患问答，不构成诊疗建议，具体请遵医嘱"
    - 禁止编造法条编号、文号、药品批准号等出处标识
    - 不得以"根据检索结果[1]"等形式引用，仅基于文本实质内容归纳分析
    - 若返回内容与问题明显不匹配，应调整 query 或切换 related 重试
    """,
    args_schema=RetrivalTool,
)
def retrieve(question: str, related: str) -> str:
    vector_db = Chroma(
        collection_name=related,
        persist_directory=str(Path(__file__).parents[1] / "Database" / "Chroma"),
        embedding_function=loader.embedding_model,

    )
    vector_retriever = vector_db.as_retriever(search_kwargs={"k": 10})

    # 打印召回结果
    def print_recall(title, docs):
        print(f"{title}到的文档内容")
        for doc in docs:
            print(doc.page_content)
        return docs

    def retriever_func(question):
        # 向量检索
        vector_result = vector_retriever.invoke(question)
        print_recall("向量检索", vector_result)
        # BM25检索
        bm25, docs = BM25Util.build_bm25_index(vector_db)
        bm25_result = BM25Util.bm25_search(bm25, question, docs, 10)
        print_recall("BM25检索", bm25_result)
        # rrf融合
        rrf_result = RRFUtil.rrf(vector_result, bm25_result)
        print_recall("RRF融合", rrf_result)
        return rrf_result
        # 加载重排序模型（复用预加载实例）

    reranker = loader.reranker

    def reranker_func(data):
        print("开始重排序")
        docs = data
        queire = [(question, doc.page_content) for doc in docs]

        scores = reranker.compute_score(queire)
        results = list(zip(docs, scores))
        # 降序
        results.sort(key=lambda x: x[1], reverse=True)
        docs_3 = [doc.page_content for doc, score in results[:3]]
        context = "\n\n".join(f"来源{i + 1}:{text}" for i, text in enumerate(docs_3))
        print(f"重排序后：{context}")
        return {'context': context,

                }

    data = retriever_func(question)
    result = reranker_func(data)
    return {
        'result': result
    }


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
# print(agent.invoke({"messages": [{"role": "user", "content": "我叫cc，你是谁？"}]}))
# print("==================================")
# print(agent.invoke({"messages": [{"role": "user", "content": "重庆天气如何"}]}))
# print("==================================")
# a=agent.invoke({"messages": [{"role": "user", "content": "糖尿病的介绍"}]})
# b=agent.stream({"messages": [{"role": "user", "content": "土地被占用了怎么办"}]})




