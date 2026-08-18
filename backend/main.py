from fastapi import FastAPI

app = FastAPI()
from Login.controller.RegisterController import register_router
app.include_router(
    router=register_router,
    prefix='/register',
    tags=['Register']
)
from Login.controller.LoginController import Login_router
app.include_router(
    router=Login_router,
    prefix='/login',
    tags=['Login']
)
from Chat.controller.HistoryController import History_router
app.include_router(
    router=History_router,
    prefix='/history',
    tags=['History']
)

from Chat.controller.ChatController import chat_router
app.include_router(
    router=chat_router,
    prefix='/chat',
    tags=['Chat']
)
from Chat.controller.DeleteHistoryController import delete_router
app.include_router(
    router=delete_router,
    prefix='/delete',
    tags=['Delete']
)
from Chat.controller.SearchHistoryController import search_history_router
app.include_router(
    router=search_history_router,
    prefix='/search',
    tags=['Search']
)
from Admin.controller.AdminController import admin_router
app.include_router(
    router=admin_router,
    prefix='/admin',
    tags=['admin']
)

#跨域配置
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)