from fastapi import Header, HTTPException
from Common import JwtUtil


# allowed_roles：允许访问的用户角色列表
def has_roles(*allowed_roles: list):
    # 判定当前用户是否有访问权限
    def user_permission(authorization: str = Header(None)):
        if not authorization or " " not in authorization:   # 案例缺这个判断，不带 header 会 500
            raise HTTPException(status_code=401, detail="未登录")
        token = authorization.split(" ")[1]
        # 获取当前用户信息
        current_user = JwtUtil.get_current_user(token)
        # 判定 --- 案例是 role_name，你的表字段是 permission
        if current_user['permission'] in allowed_roles[0]:
            return current_user
        else:
            raise HTTPException(status_code=403, detail="无访问权限")

    return user_permission
