"""
文档处理模型
"""
import os
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Document:
    """文档数据模型"""
    id: str
    filename: str
    content: str
    metadata: dict
    
class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self):
        self.supported_extensions = ['.txt']
    
    def extract_text(self, file_path: str) -> str:
        """从文件中提取文本"""
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.txt':
            return self._extract_text_file(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {ext}")
    
    def _extract_text_file(self, file_path: str) -> str:
        """提取文本文件内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """将文本分块"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # 尝试在句号处分割
            split_point = text.rfind('.', start, end)
            if split_point == -1:
                split_point = end
            
            chunks.append(text[start:split_point + 1])
            start = split_point + 1 - overlap
            
        return chunks 