from py2neo import Graph
import os
from dotenv import load_dotenv
load_dotenv()

def get_neo4j_conn():
    return Graph(
        profile = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "844282963")),#用户密码
        name = os.getenv("NEO4J_DATABASE", "neo4j")#Database
    )

