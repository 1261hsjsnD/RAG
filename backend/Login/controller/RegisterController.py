from fastapi import APIRouter
from Login.service import  RegisterService
register_router = APIRouter()
from pydantic import BaseModel,Field
from Login.dao import RegisterDao

@register_router.get('/register')
def register(email:str):
    return RegisterService.register(email)
@register_router.get('/check')
def check(email:str,code:str):
    return RegisterService.check_email(email,code)


class CreateUser(BaseModel):
    email: str = Field(..., title="用户邮箱"),
    username:str=Field(...,title="用户名"),
    password: str = Field(..., title="用户密码"),
@register_router.post('/creat')
def create(CreateUser: CreateUser):
    email = CreateUser.email
    username = CreateUser.username
    password=CreateUser.password
    return RegisterService.create(email,username,password)
