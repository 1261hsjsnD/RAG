from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse
from Common import JwtUtil
from Chat.service import ChatService
import json

chat_router = APIRouter()

@chat_router.get("/chat")
def chat(question: str, historyId: int, user: dict = Depends(JwtUtil.get_current_user)):
    # token 从请求头 Authorization: Bearer xxx 中自动取出并验证：
    # 1. 验签（过期/伪造抛 401） 2. Redis 白名单检查（登出/失效抛 401）
    # user 即解码后的 payload，包含 email/username/permission
    print(f"当前用户：{user}")

    # 流式输出处理
    def generator():
        for chunk in ChatService.chat(question, historyId):
            yield f"data:{json.dumps({'content': chunk})}\n\n"
        yield f"data:{json.dumps({'content': '[DONE]'})}\n\n"

    return StreamingResponse(
        content=generator(),
        media_type="text/event-stream",
    )