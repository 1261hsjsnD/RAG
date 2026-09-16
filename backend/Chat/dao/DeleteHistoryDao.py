from Common import MySQLUtil

def deleteHistoryDao(history_id,email):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "delete from `history` where (history_id=%s or parent_id=%s) and email=%s"
        cur.execute(sql, (history_id, history_id, email))
        conn.commit()
        return True
    except Exception as e:
        print(f"删除失败{e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()