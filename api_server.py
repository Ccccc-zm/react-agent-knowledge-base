# api_server.py
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中，避免导入 agent 模块时出错
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.react_agent import ReactAgent


# 创建 FastAPI 应用
app = FastAPI(
    title="智能客服 API",
    description="基于 LangGraph 的 ReAct Agent 对话接口",
    version="1.0.0"
)

# 允许跨域（便于前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 生产环境请指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局单例 Agent，避免重复加载模型
agent = ReactAgent()

class ChatRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "智能客服 API 运行中，请使用 POST /chat/stream 或 /chat"}

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """流式对话接口，返回纯文本流"""
    def generate():
        for chunk in agent.execute_stream(req.query):
            yield chunk
    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/chat")
async def chat(req: ChatRequest):
    """非流式对话接口，返回完整 JSON"""
    full_response = ""
    for chunk in agent.execute_stream(req.query):
        full_response += chunk
    return {"response": full_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)