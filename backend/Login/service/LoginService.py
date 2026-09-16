from Common import MySQLUtil,JwtUtil

def login(email,password):
    conn=MySQLUtil.get_mysql_conn()
    cursor=conn.cursor()
    SQL='select password,username,email,permission from users where email=%s'
    cursor.execute(SQL,[email])
    result=cursor.fetchall()
    cursor.close()
    conn.close()
    if result:
        word=result[0]['password']
        #生成jwtID做黑名单处理，
        if JwtUtil.verify_password(password,word):
            token = JwtUtil.create_access_token({
            "email":result[0]['email'],
            "username":result[0]['username'],
            "permission": result[0]['permission']
            })
            return {
                "code":200,
                "msg":"登录成功",
                "token":token,
                "email":result[0]['email'],
                "username":result[0]['username'],
                "permission": result[0]['permission']
            }
        else:
            return {
                "code": 400,
                "msg": "密码错误"
            }
    else:
        return{
            "code":404,
            "msg":"请检查邮箱"
        }

if __name__ == '__main__':
    email='1'
    password="1"
    print(login(email,password))
