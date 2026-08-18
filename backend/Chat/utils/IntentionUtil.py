import json

from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv
load_dotenv()
def intention_recogntion(question):
    llm=ChatOllama(
        model=os.getenv("OLLAMA_MODEL_NAME"),
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )
    #提示词
    prompt="""
    
    你是一个领域分类器。你的唯一任务是判断用户的问题属于以下哪个领域：法律、医疗、或都不相关。

分类规则：
- law：问题涉及法律法规、法律条文、合同纠纷、诉讼程序、法律责任、知识产权保护、劳动法、婚姻法等法律相关话题
- medical：问题涉及疾病症状、诊断治疗、药物用药、手术、医学检查、健康管理、心理健康等医疗相关话题
- none：问题既不属于法律也不属于医疗，或无法明确归入以上两类

核心判断原则（优先级从高到低）：
1. 如果问题同时涉及法律和医疗（如医疗纠纷、医院打人、医疗事故索赔、医患矛盾等），必须归类为 law
2. 如果问题描述了一个发生在医疗场景中的事件，但用户的核心诉求是追究责任、寻求法律帮助、了解处罚后果，归类为 law
3. 只有当用户的核心诉求是了解疾病、治疗、用药、检查等纯医学问题时，才归类为 medical
4. 只根据问题本身的内容判断，不要过度联想
5. 不要对问题做任何回答或解释

输出要求：
- 只能输出一个合法的JSON对象，不包含任何其他文字、解释或标记
- 如果分类结果为 law 或 medical，输出包含 "related" 键的对象
- 如果分类结果为 none，输出空JSON对象 {}(注意不要输出{'related': 'none'}) 
- JSON中 "related" 的值只能是 "law" 或 "media"

输出示例结果只能为下面3个之一：
{"related": "law"}
{"related": "medical"}
{}  

用户问题：{question}
    
    
    """
    rs =llm.invoke([
        {"role": "system", "content": prompt},
        {"role": "user", "content": question}
            ])
    return json.loads(rs.content)

if __name__ == '__main__':
    question="你好"
    print(intention_recogntion(question))