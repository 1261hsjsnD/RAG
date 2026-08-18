from Chat.dao import DeleteHistoryDao
from Common import RedisUtil
def delete_history(history_id):
    return DeleteHistoryDao.deleteHistoryDao(history_id)


def logout(token):
    r = RedisUtil.get_redis_client()
    r.delete(token)
    r.close()
    return{
        "code":200,
        "msg":"退出成功",

    }