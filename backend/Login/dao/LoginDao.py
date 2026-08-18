from Common import MySQLUtil
def login(email, password):
    conn= MySQLUtil.get_mysql_conn()
    cur= conn.cursor()
    SQL='select email,password from users where email=%s and password=%s'
    cur.execute(SQL,[email,password])
    result=cur.fetchall()
    cur.close()
    conn.close()
    return result
if __name__ == '__main__':
    email='844282963@qq.com'
    password="844282963"
    print(login(email,password))