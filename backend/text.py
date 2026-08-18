# #密钥生成
# import secrets
# #生成32位
# key =secrets.token_urlsafe(32)
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Annotated

#创建CryptContext对象
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#密码加密
def hash_password(password:str) -> str:
    return crypt_context.hash(password)

#密码对比，加密后比对
def verify_password(password:str, hashed_password:str) -> bool:
    return crypt_context.verify(password, hashed_password)





from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

#生成token---data:用户封装进的数据类容格式字典
def create_access_token(data:dict)->str:
    #拷贝
    copy_data=data.copy()
    #设置过期时间
    expire=datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    #添加过期时间
    copy_data.update({'exp': expire,"iat":datetime.now(timezone.utc)})
    '''
    入库，退出时删除
    
    '''
    #生成
    return jwt.encode(
        claims=copy_data,
        key=os.getenv('SECRET_KEY'),#密钥
        algorithm=os.getenv('ALGORITHM')#算法
    )


#验证
def verify_token(token:str)->dict:
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")]
        )
        return payload
    except JWTError:
        return {
            "code":401,
            "msg":"token已过期或错误"
        }



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
#解码
"""
Depends:在进入这个方法时，要依赖于oauth2_scheme方法，等价于拦截处理

"""
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)])->dict:
    #解析token获取用户数据
    payload = verify_token(token)
    #过期处理
    if payload is None:
        return
    user_id=int(payload["user_id"])
    #判断-----假设数据
    if user_id is None:
        return None
