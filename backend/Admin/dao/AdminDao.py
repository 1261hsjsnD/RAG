from Common import MySQLUtil
from Chat.dao import DeleteHistoryDao
def updata():
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    SQL="select users_id,username,email,create_time,permission from users "
    cur.execute(SQL)
    data=cur.fetchall()
    for row in data:
        if row.get("create_time"):
            row["create_time"] = row["create_time"].strftime("%Y-%m-%d %H:%M:%S")
    cur.close()
    conn.close()
    return data


def delete(email):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "delete from  `users` where email = %s"
        SQL = "delete from `history` where email=%s"
        cur.execute(sql, [email])
        cur.execute(SQL, [email])
        conn.commit()
        return True
    except Exception as e:
        print(f"删除失败: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()




def submit_updata(updateList):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "update `users` set permission = %s where users_id = %s"
        params = [(item["permission"], item["users_id"]) for item in updateList]
        cur.executemany(sql, params)
        conn.commit()
        return True
    except Exception as e:
        print(f"批量更新权限失败: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
if __name__ == '__main__':
    print(submit_updata([
        {"users_id": 1, "permission": "admin"},
        {"users_id": 4, "permission": "users"},
        {"users_id": 9, "permission": "users"}
    ]))