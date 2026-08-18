
from Chat.dao import HistorySearchDao
def searchHistory(word,email):
    return HistorySearchDao.history_search(word,email)

