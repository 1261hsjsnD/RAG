import redis
import os
import dotenv
dotenv.load_dotenv()
def get_redis_client():
    return redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'),
        db=int(os.getenv('REDIS_DB')),
        protocol=2,
        decode_responses = True#可以把输出类型自动转换为str
    )
