"""
文档处理模型
"""
import os
import PyPDF2
import docx
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
        self.supported_extensions = ['.txt', '.pdf', '.docx', '.md']
    
    def extract_text(self, file_path: str) -> str:
        """从文件中提取文本"""
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.txt' or ext == '.md':
            return self._extract_text_file(file_path)
        elif ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext == '.docx':
            return self._extract_docx(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {ext}")
    
    def _extract_text_file(self, file_path: str) -> str:
        """提取文本文件内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_pdf(self, file_path: str) -> str:
        """提取PDF文件内容"""
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_docx(self, file_path: str) -> str:
        """提取DOCX文件内容"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
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