"""
配置文件 - 私人知识库系统
"""

# Ollama配置
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:1.5b"

# 向量数据库配置
CHROMA_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# 文档处理配置
UPLOAD_DIR = "./uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_EXTENSIONS = ['.txt']

# 检索配置
TOP_K_RESULTS = 5
MAX_CONTEXT_LENGTH = 2000

# API配置
API_HOST = "0.0.0.0"
API_PORT = 8000 