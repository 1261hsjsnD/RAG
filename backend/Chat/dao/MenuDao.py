from Common import MySQLUtil
from Chat.utils import IntentionUtil
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
def history_dao(history_id,email):
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    SQL="select question,answer from history where (history_id=%s or parent_id=%s) and email=%s "
    cur.execute(SQL,[history_id,history_id,email])
    result=cur.fetchall()
    cur.close()
    conn.close()
    #处理输出结果
    history_list=[]
    a = len(result)

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
def history_dao2(history_id,email):
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    SQL="select question,answer from history where history_id=%s or parent_id=%s order by create_time desc"
    cur.execute(SQL,[history_id,history_id])
    result=cur.fetchall()
    #只返回最近五条内没有被压缩的
    a =len(result)
    c = a%5
    cur.close()
    conn.close()
    #处理输出结果
    history_list=[]
    #压缩的历史记录
    a =summary_history(history_id,email)
    history_list.append({'role':'system','content':f'这是经过压缩的历史记录对话{a}'})

    if c !=0:
        for item in result[:c]:
            history_list.append({
                "role":"user",
                "content":item["question"],
            })
            history_list.append({
                "role":"assistant",
                "content":item["answer"],
            })
        # print(history_list)
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
        summary_history_dao(parent_id, email)
        return cur.lastrowid
    except Exception as e:
        print(f"失败{e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()



#history做压缩每5论压缩一遍，只返回最近5论的完整对话
def summary_history_dao(historyId,email):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    sql="select question,answer from history where history_id=%s or parent_id=%s order by create_time asc, history_id asc"
    cur.execute(sql,[historyId,historyId])
    result=cur.fetchall()
    #每五轮压缩一次
    a =len(result)%5
    try:
        if historyId!=0:
            if a== 0:
                message=result[-5:]
                return IntentionUtil.summary_llm(message,historyId,email)
    except Exception as e:
        conn.rollback()
        print(e)
    finally:
        cur.close()
        conn.close()

#压缩的历史记录
def summary_history(historyId,email):
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    sql="select compress from summary where history_id=%s and email=%s"
    cur.execute(sql,[historyId,email])
    result=cur.fetchall()
    return result


if __name__ == '__main__':
    print(summary_history(24,1))





