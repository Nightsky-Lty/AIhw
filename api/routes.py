"""
API路由定义
"""
import os
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.knowledge_base import KnowledgeBase
from services.ollama_service import OllamaService
from services.folder_watcher import FolderWatcher
import config

router = APIRouter()

# 初始化服务
kb = KnowledgeBase()
ollama = OllamaService()
folder_watcher = FolderWatcher(kb)  # 默认会自动启动监控

# 创建上传目录
os.makedirs(config.UPLOAD_DIR, exist_ok=True)

class QuestionRequest(BaseModel):
    question: str
    use_context: bool = True

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    use_context: bool = True

# 文件夹监控相关接口

@router.post("/folder-watch/start")
async def start_folder_watching():
    """启动文件夹监控"""
    try:
        folder_watcher.start_watching()
        return JSONResponse({
            "success": True,
            "message": "文件夹监控已启动",
            "watch_folder": str(folder_watcher.watch_folder.absolute())
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动监控失败: {str(e)}")

@router.post("/folder-watch/stop")
async def stop_folder_watching():
    """停止文件夹监控"""
    try:
        folder_watcher.stop_watching()
        return JSONResponse({
            "success": True,
            "message": "文件夹监控已停止"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止监控失败: {str(e)}")

@router.get("/folder-watch/status")
async def get_folder_watch_status():
    """获取文件夹监控状态"""
    try:
        status = folder_watcher.get_status()
        return JSONResponse({
            "success": True,
            "status": status
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@router.post("/folder-watch/rescan")
async def force_rescan_folder():
    """强制重新扫描文件夹"""
    try:
        folder_watcher.force_rescan()
        return JSONResponse({
            "success": True,
            "message": "强制重新扫描完成"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新扫描失败: {str(e)}")

@router.post("/question")
async def ask_question(request: QuestionRequest):
    """问答接口"""
    try:
        context = []
        if request.use_context:
            # 搜索相关文档
            search_results = kb.search(request.question, config.TOP_K_RESULTS)
            context = [result['content'] for result in search_results]
        
        # 生成回答
        answer = ollama.generate_response(request.question, context)
        
        return JSONResponse({
            "success": True,
            "question": request.question,
            "answer": answer,
            "context_used": len(context) > 0,
            "sources": len(context)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")

@router.post("/chat")
async def chat(request: ChatRequest):
    """多轮对话接口"""
    try:
        context = []
        if request.use_context and request.messages:
            # 使用最后一条消息搜索上下文
            last_message = request.messages[-1].content
            search_results = kb.search(last_message, config.TOP_K_RESULTS)
            context = [result['content'] for result in search_results]
        
        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # 生成回答
        answer = ollama.chat_with_context(messages, context)
        
        return JSONResponse({
            "success": True,
            "answer": answer,
            "context_used": len(context) > 0,
            "sources": len(context)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@router.get("/documents")
async def list_documents():
    """获取文档列表"""
    try:
        documents = kb.list_documents()
        return JSONResponse({
            "success": True,
            "documents": documents
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """删除文档"""
    try:
        success = kb.delete_document(document_id)
        if success:
            return JSONResponse({
                "success": True,
                "message": "文档删除成功"
            })
        else:
            raise HTTPException(status_code=404, detail="文档不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")

@router.get("/search")
async def search_documents(q: str, limit: int = 5):
    """搜索文档"""
    try:
        results = kb.search(q, limit)
        return JSONResponse({
            "success": True,
            "query": q,
            "results": results
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/stats")
async def get_stats():
    """获取知识库统计信息"""
    try:
        stats = kb.get_stats()
        return JSONResponse({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查Ollama模型
        model_available = ollama.check_model_availability()
        
        return JSONResponse({
            "success": True,
            "status": "healthy",
            "ollama_available": model_available,
            "model": config.OLLAMA_MODEL
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }) 