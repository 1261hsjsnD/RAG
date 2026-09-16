from fastapi import APIRouter, Depends
from Chat.service import SearchHistoryService
from Common import JwtUtil

search_history_router = APIRouter()
@search_history_router.get('/searchHistory')
def searchHistory(word:str,user: dict = Depends(JwtUtil.get_current_user)):
    email = user['email']
    return SearchHistoryService.searchHistory(word,email)