"""
私人知识库系统 - 主应用
基于FastAPI + ChromaDB + Ollama DeepSeek
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import os

from api.routes import router
import config

# 创建FastAPI应用
app = FastAPI(
    title="私人知识库系统",
    description="基于Ollama DeepSeek的智能问答知识库",
    version="1.0.0"
)

# 挂载API路由
app.include_router(router, prefix="/api", tags=["知识库API"])

# 创建静态文件和模板目录
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/docs-ui", response_class=HTMLResponse)
async def docs_ui(request: Request):
    """文档管理页面"""
    return templates.TemplateResponse("docs.html", {"request": request})

@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    """聊天页面"""
    return templates.TemplateResponse("chat.html", {"request": request})

if __name__ == "__main__":
    print("🚀 启动私人知识库系统...")
    print(f"📝 Web界面: http://{config.API_HOST}:{config.API_PORT}")
    print(f"📚 API文档: http://{config.API_HOST}:{config.API_PORT}/docs")
    print(f"🤖 Ollama模型: {config.OLLAMA_MODEL}")
    
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    ) 