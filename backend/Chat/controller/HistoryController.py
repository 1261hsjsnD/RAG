from fastapi import APIRouter,Depends
from Common import JwtUtil
from Chat.service import HistoryService

History_router = APIRouter()
@History_router.get('/menu')
def menu_updata(user: dict = Depends(JwtUtil.get_current_user)):
    # email 一律从 token 取，不信任前端传入
    email = user['email']
    return HistoryService.menu_updata(email)
@History_router.get('/history')
def history(historyId,user: dict = Depends(JwtUtil.get_current_user)):
    # email 从 token 取，DAO 层按 email 过滤，防止越权读取他人历史
    email = user['email']
    return HistoryService.history(historyId,email)
@History_router.get('/save')
def save_history(question,answer,parent_id,user: dict = Depends(JwtUtil.get_current_user)):
    # email 从 token 取，防止伪造他人 email 写入历史
    email = user['email']
    return HistoryService.save_history(email,question,answer,parent_id)