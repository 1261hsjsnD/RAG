from fastapi import APIRouter,Depends
from Common import JwtUtil
from Chat.service import HistoryService

History_router = APIRouter()
@History_router.get('/menu')
def menu_updata(email,user: dict = Depends(JwtUtil.get_current_user)):
    return HistoryService.menu_updata(email)
@History_router.get('/history')
def history(historyId,user: dict = Depends(JwtUtil.get_current_user)):
    return HistoryService.history(historyId)
@History_router.get('/save')
def save_history(email,question,answer,parent_id,user: dict = Depends(JwtUtil.get_current_user)):
    return HistoryService.save_history(email,question,answer,parent_id)