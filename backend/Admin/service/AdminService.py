from Admin.dao import AdminDao

def updata(permission):
    return AdminDao.updata()


def delete(email):
    return AdminDao.delete(email)


def submit_update(updateList):
    return AdminDao.submit_updata(updateList)