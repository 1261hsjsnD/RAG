from fastapi import APIRouter, Depends

from Chat.service import DeletHistoryService
from Common import JwtUtil

delete_router = APIRouter()
#删除历史记录
@delete_router.get('/delete')
def delete_history(history_id: int,user: dict = Depends(JwtUtil.get_current_user)):
    # email 从 token 取，DAO 层按 email 过滤，防止越权删除他人记录
    email = user['email']
    return DeletHistoryService.delete_history(history_id,email)

#点击退出删除redis里面的键
@delete_router.get('/logout')
def logout(token: str,user: dict = Depends(JwtUtil.get_current_user)):
    return DeletHistoryService.logout(token)