from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .model import llm_handler
import logging

app = FastAPI(title="LLM API", description="大语言模型API服务")
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = None
    temperature: Optional[float] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

class ErrorResponse(BaseModel):
    error: str
    status: str = "error"

@app.on_event("startup")
async def startup_event():
    """服务启动时加载模型"""
    success = await llm_handler.load_model()
    if not success:
        logger.error("模型加载失败")
        raise RuntimeError("模型加载失败")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "model_loaded": llm_handler.model is not None
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    try:
        response = await llm_handler.generate_response(
            request.prompt,
            request.max_length,
            request.temperature
        )
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"处理请求失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 