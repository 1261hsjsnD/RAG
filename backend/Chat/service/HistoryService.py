from Chat.dao import MenuDao
def menu_updata(email):
    return MenuDao.menu_dao(email)

def history(historyId,email):
    return MenuDao.history_dao(historyId,email)


def save_history(email,question,answer,parent_id):
    return MenuDao.history_save(email,question,answer,parent_id)