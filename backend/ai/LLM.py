from langchain_openai import ChatOpenAI
import os
def load_model():
    return ChatOpenAI(
    #通过环境变量中读取api-key
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    #指定基础服务地址 --- 阿里公司提供的模型访问地址
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    #指定模型名称
    model="qwen3.6-flash",
    #流式输出
    streaming=True,
    )