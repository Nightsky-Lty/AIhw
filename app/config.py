from pydantic import BaseSettings

class Settings(BaseSettings):
    # 模型配置
    MODEL_NAME = "deepseek-ai/deepseek-coder-1.3b-base"  # DEEPSEEK 1.3B模型
    MODEL_CACHE_DIR = "./model_cache"
    MAX_LENGTH = 2048
    DEFAULT_TEMPERATURE = 0.7
    
    # 服务器配置
    HOST = "0.0.0.0"
    PORT = 8000
    
    # 性能配置
    USE_ONNX = False  # DEEPSEEK模型建议关闭ONNX
    USE_INT8 = False  # 如果遇到问题可以关闭量化
    
    class Config:
        env_file = ".env"

settings = Settings() 