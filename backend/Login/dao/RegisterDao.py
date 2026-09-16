from Common import MySQLUtil,RedisUtil

def check(email):
    conn=MySQLUtil.get_mysql_conn()
    cur=conn.cursor()
    SQL="select email from users where email=%s"
    cur.execute(SQL,[email])
    result=cur.fetchall()
    cur.close()
    conn.close()
    return result

if __name__ == '__main__':
    email='844282963@qq.com'
    print(check(email)[0]["email"])