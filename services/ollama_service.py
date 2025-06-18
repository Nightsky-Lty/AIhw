"""
Ollama服务集成
"""
import requests
import json
from typing import List, Dict, Any, Optional
import config

class OllamaService:
    """Ollama服务管理器"""
    
    def __init__(self):
        self.host = config.OLLAMA_HOST
        self.model = config.OLLAMA_MODEL
    
    def generate_response(self, prompt: str, context: List[str] = None) -> str:
        """生成回答"""
        try:
            # 构建完整的提示词
            full_prompt = self._build_prompt(prompt, context)
            
            # 调用Ollama API
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '抱歉，无法生成回答。')
            else:
                raise Exception(f"Ollama API错误: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"连接Ollama服务失败: {str(e)}")
        except Exception as e:
            raise Exception(f"生成回答失败: {str(e)}")
    
    def _build_prompt(self, question: str, context: List[str] = None) -> str:
        """构建提示词"""
        prompt = "你是一个智能助手，请根据提供的上下文信息回答用户的问题。\n\n"
        
        if context:
            prompt += "相关上下文信息：\n"
            for i, ctx in enumerate(context, 1):
                prompt += f"{i}. {ctx}\n\n"
        
        prompt += f"用户问题：{question}\n\n"
        prompt += "请基于上述上下文信息回答问题。如果上下文信息不足以回答问题，请说明这一点。\n\n回答："
        
        return prompt
    
    def check_model_availability(self) -> bool:
        """检查模型是否可用"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'] == self.model for model in models)
            return False
        except:
            return False
    
    def chat_with_context(self, messages: List[Dict[str, str]], context: List[str] = None) -> str:
        """支持多轮对话的聊天功能"""
        try:
            # 构建对话历史
            conversation = ""
            for msg in messages[-5:]:  # 只保留最近5轮对话
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conversation += f"{role}: {content}\n"
            
            # 添加上下文
            if context:
                conversation = "参考信息：\n" + "\n".join(context) + "\n\n" + conversation
            
            # 生成回答
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": conversation + "assistant: ",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '抱歉，无法生成回答。')
            else:
                raise Exception(f"Ollama API错误: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"对话失败: {str(e)}") 