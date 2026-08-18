from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from Common import RedisUtil
load_dotenv()

#创建CryptContext对象
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#密码加密
def hash_password(password:str) -> str:
    return crypt_context.hash(password)

#密码对比，加密后比对
def verify_password(password:str, hashed_password:str) -> bool:
    return crypt_context.verify(password, hashed_password)


# 生成token---data:用户封装进的数据类容格式字典
def create_access_token(data: dict) -> str:
    # 拷贝
    copy_data = data.copy()
    # 设置过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    # 添加过期时间
    copy_data.update({'exp': expire, "iat": datetime.now(timezone.utc)})
    '''
    入库，退出时删除

    '''
    # 生成
    jwt_result= jwt.encode(
        claims=copy_data,
        key=os.getenv('SECRET_KEY'),  # 密钥
        algorithm=os.getenv('ALGORITHM')  # 算法
    )
    r=RedisUtil.get_redis_client()
    r.set(jwt_result,"1", ex=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')) * 60)
    r.close()

    return jwt_result

#验证方法解密
def verify_token(token:str)->dict:
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="token已过期或错误")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/login")
#
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    payload = verify_token(token)
    r = RedisUtil.get_redis_client()
    if r.exists(token) != 1:
        raise HTTPException(401, "登录已失效，请重新登录")
    return payload
