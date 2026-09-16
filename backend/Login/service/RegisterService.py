from email.mime.text import MIMEText
import smtplib
import time
from Common import RedisUtil,MySQLUtil
from Login.dao import RegisterDao
import random
import os
from dotenv import load_dotenv
load_dotenv()
from Common import JwtUtil
#发送验证码
def register(email:str):
    if not RegisterDao.check(email):
        #配置信息
        sender= os.getenv("SENDER_EMAIL")
        psw=os.getenv("SENDER_EMAIL_PASSWORD")
        subject="注册验证码请接收"
        #随机验证码
        code=""
        for i in range(4):
            code+=str(int(random.random()*10))
        content=f"您正在注册我司账号，验证码是:{code},请在一分钟内输入"
        message=MIMEText(
            content,
            _subtype='plain',
            _charset='utf-8'
        )
        message["From"]=sender
        message["To"]=email
        message["Subject"]=subject



        try:
            #发送邮件对象
            smtp=smtplib.SMTP(
                host=os.getenv("SMTP_HOST"),
                port=int(os.getenv("SMTP_PORT")),
            )
            smtp.starttls(),#升级TLS加密
            smtp.login(sender,psw),
            smtp.sendmail(
                sender,
                email,
                message.as_string()
            )
            smtp.quit()
            #与Redis库建立连接，存入验证码
            r = RedisUtil.get_redis_client()
            r.set(email,code,ex=60)
            r.close()
            return{
                "code":200,
                "msg":"发送成功",
                "email":email,


            }
        except Exception as e:
            print(f'邮件发送失败{e}')
            return{
                "code": 500,
                "msg": "发送失败",
                "data": None,
            }
    else:

        return{
            "code":400,
            "msg":"邮箱已被注册",
            "data":None,

        }
#验证验证码
def check_email(email,code):
    r = RedisUtil.get_redis_client()
    if r.get(email)==None:
        r.close()
        return{"code":404,
            "msg":"验证码已过期"}
    else:
        True_code=r.get(email)
        if code ==True_code:
            #封装token只让通过验证的邮箱可以注册
            token=JwtUtil.generate_token(email)
            #验证码使用完毕立即删除
            r.delete(email)
            r.close()
            return{"code":200,
                "msg":"验证成功",
                "token":token,
            }
        else:
            r.close()
            return {"code":500,"msg":"验证码错误"}
#创建
def create(email,username,password,token):
    #1.校验注册token，防止未验证邮箱直接注册
    try:
        payload=JwtUtil.verify_token(token)
    except Exception:
        return{"code":401,"msg":"token已过期或错误，请重新验证"}
    #2.token里的邮箱必须与本次注册邮箱一致
    if payload.get("email")!=email:
        return{"code":401,"msg":"邮箱与验证邮箱不一致，请重新验证"}
    #3.token必须未被使用（一次性），防止重放
    r = RedisUtil.get_redis_client()
    if r.exists(token)!=1:
        r.close()
        return{"code":401,"msg":"验证已失效，请重新验证"}
    r.close()
    #4.销毁token，注册token只能使用一次
    JwtUtil.delete_token(token)
    #包装密码
    password= JwtUtil.hash_password(password)
    try:
        conn=MySQLUtil.get_mysql_conn()
        cursor=conn.cursor()
        SQL="insert into users(email,username,password,permission) values(%s,%s,%s,'users')"
        cursor.execute(SQL,(email,username,password))

        conn.commit()

        return{
            "code":200,
            "msg":"创建成功"
        }
    except Exception as e:
        return {'code':500,
                'msg':f"创建失败{e}"}
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    password="844282963"
    print(JwtUtil.hash_password(password))