from fastapi import APIRouter, Depends,HTTPException
from typing import List
from Admin.service import AdminService
from Common import JwtUtil

admin_router = APIRouter()
@admin_router.get("/updata")
def updata(permission:str,user: dict = Depends(JwtUtil.get_current_user)):
    if user.get("permission") != "admin":
        raise HTTPException(status_code=403, detail="无管理员权限")
    return AdminService.updata(permission)
@admin_router.get("/delete")
def delete(email:str,user: dict = Depends(JwtUtil.get_current_user)):
    if user.get("permission") != "admin":
        raise HTTPException(status_code=403, detail="无管理员权限")
    return AdminService.delete(email)
@admin_router.post("/submit")
def submit_update(updateList: List[dict],user: dict = Depends(JwtUtil.get_current_user)):
    if user.get("permission") != "admin":
        raise HTTPException(status_code=403, detail="无管理员权限")
    return AdminService.submit_update(updateList)