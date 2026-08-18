from Common import MySQLUtil
#菜单
def menu_dao(email):
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    SQL="select question,create_time,history_id from history where email=%s and parent_id=0 order by create_time desc"
    cur.execute(SQL,[email])
    result=cur.fetchall()
    cur.close()
    conn.close()
    return result

#某条记录下的所有History
def history_dao(history_id):
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    SQL="select question,answer from history where history_id=%s or parent_id=%s"
    cur.execute(SQL,[history_id,history_id])
    result=cur.fetchall()
    cur.close()
    conn.close()
    #处理输出结果
    history_list=[]
    for item in result:
        history_list.append({
            "role":"user",
            "content":item["question"],
        })
        history_list.append({
            "role":"assistant",
            "content":item["answer"],
        })
    return {
        "code":200,
        "data":history_list
    }


def history_save(email,question,answer,parent_id):
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    SQL="insert into `history` values(null,%s,%s,%s,%s,now()) "
    try:
        cur.execute(SQL,[email,question,answer,parent_id])
        conn.commit()

        return cur.lastrowid
    except Exception as e:
        print(f"失败{e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
if __name__ == '__main__':

   a=menu_dao('1')
   print( a)


