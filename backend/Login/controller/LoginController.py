from fastapi import APIRouter

from Login.service import LoginService
from pydantic import BaseModel,Field
Login_router = APIRouter()
class Logincheck(BaseModel):
    email: str=Field(...,title="用户邮箱")
    password:str=Field(...,title="用户密码")
@Login_router.post('/login')
def login(Logincheck: Logincheck):
    email=Logincheck.email
    password=Logincheck.password
    return LoginService.login(email,password)