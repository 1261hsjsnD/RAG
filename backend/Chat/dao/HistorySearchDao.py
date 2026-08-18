from Common import MySQLUtil
#菜单查询
def history_search(word,email):
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    SQL="select history_id,parent_id from history where question like %s"
    cur.execute(SQL,["%"+word+"%"])
    result=cur.fetchall()
    #用集合去重
    c = set()
    for item in result:

        a=[item["history_id"],item["parent_id"]]
        if a[1]!=0:
            c.add(a[1])
        else:
            c.add(a[0])
    #存放结果
    c=list(c)
    print(c)
    print("------------")
    d =[]

    for i in c:
        SQL="select question,create_time,history_id from history where history_id=%s and email=%s "
        cur.execute(SQL,[i,email])
        result=cur.fetchall()
        print(result)
        if result:
            d.append(result[0])
    print(d)
    print("------------")
    cur.close()
    conn.close()
    d.sort(key = lambda x:x['history_id'],reverse=True)
    return d

if __name__ == '__main__':
    print(history_search("天气","1"))