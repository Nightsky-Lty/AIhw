"""
知识库核心模型
"""
import os
import uuid
from typing import List, Dict, Any, Optional
from .document import DocumentProcessor, Document
import config

# 可选依赖导入
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    print("警告: ChromaDB未安装，将使用简单的内存存储")
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("警告: sentence-transformers未安装，将使用简单的文本匹配")
    EMBEDDINGS_AVAILABLE = False

class SimpleKnowledgeBase:
    """简化版知识库（无向量搜索）"""
    
    def __init__(self):
        self.documents = {}  # 存储文档 {doc_id: {"filename": str, "chunks": [str]}}
        self.doc_processor = DocumentProcessor()
    
    def add_document(self, file_path: str, filename: str) -> str:
        """添加文档"""
        try:
            text = self.doc_processor.extract_text(file_path)
            chunks = self.doc_processor.chunk_text(text)
            doc_id = str(uuid.uuid4())
            
            self.documents[doc_id] = {
                "filename": filename,
                "chunks": chunks
            }
            return doc_id
        except Exception as e:
            raise Exception(f"添加文档失败: {str(e)}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """简单文本搜索"""
        results = []
        query_lower = query.lower()
        
        for doc_id, doc_data in self.documents.items():
            for i, chunk in enumerate(doc_data["chunks"]):
                if query_lower in chunk.lower():
                    results.append({
                        "content": chunk,
                        "metadata": {
                            "document_id": doc_id,
                            "filename": doc_data["filename"],
                            "chunk_index": i
                        },
                        "similarity": 0.8  # 固定相似度
                    })
        
        return results[:top_k]
    
    def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """列出文档"""
        return [
            {
                "id": doc_id,
                "filename": doc_data["filename"],
                "chunk_count": len(doc_data["chunks"])
            }
            for doc_id, doc_data in self.documents.items()
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_chunks = sum(len(doc_data["chunks"]) for doc_data in self.documents.values())
        return {
            "total_chunks": total_chunks,
            "total_documents": len(self.documents),
            "documents": self.list_documents()
        }

class KnowledgeBase:
    """知识库管理器"""
    
    def __init__(self):
        if CHROMADB_AVAILABLE and EMBEDDINGS_AVAILABLE:
            self._init_advanced()
        else:
            self._init_simple()
        
        # 初始化文档处理器
        self.doc_processor = DocumentProcessor()
    
    def _init_advanced(self):
        """初始化高级版本（ChromaDB + 向量搜索）"""
        self.mode = "advanced"
        self.chroma_client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.collection = self.chroma_client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
    
    def _init_simple(self):
        """初始化简化版本（内存存储 + 文本搜索）"""
        self.mode = "simple"
        self.simple_kb = SimpleKnowledgeBase()
    
    def add_document(self, file_path: str, filename: str) -> str:
        """添加文档到知识库"""
        if self.mode == "simple":
            return self.simple_kb.add_document(file_path, filename)
        
        try:
            # 提取文本
            text = self.doc_processor.extract_text(file_path)
            
            # 分块
            chunks = self.doc_processor.chunk_text(text)
            
            # 生成文档ID
            doc_id = str(uuid.uuid4())
            
            # 为每个块生成嵌入并添加到向量数据库
            embeddings = []
            chunk_ids = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                embedding = self.embedding_model.encode(chunk).tolist()
                
                chunk_ids.append(chunk_id)
                embeddings.append(embedding)
                metadatas.append({
                    "document_id": doc_id,
                    "filename": filename,
                    "chunk_index": i,
                    "chunk_count": len(chunks)
                })
            
            # 添加到ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            return doc_id
            
        except Exception as e:
            raise Exception(f"添加文档失败: {str(e)}")
    
    def search(self, query: str, top_k: int = config.TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """搜索相关文档"""
        if self.mode == "simple":
            return self.simple_kb.search(query, top_k)
        
        try:
            # 生成查询嵌入
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # 搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # 格式化结果
            search_results = []
            for i in range(len(results['documents'][0])):
                search_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": 1 - results['distances'][0][i]  # 转换为相似度分数
                })
            
            return search_results
            
        except Exception as e:
            raise Exception(f"搜索失败: {str(e)}")
    
    def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        if self.mode == "simple":
            return self.simple_kb.delete_document(document_id)
        
        try:
            # 查找所有相关的块
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                # 删除所有块
                self.collection.delete(ids=results['ids'])
                return True
            return False
            
        except Exception as e:
            raise Exception(f"删除文档失败: {str(e)}")
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档"""
        if self.mode == "simple":
            return self.simple_kb.list_documents()
        
        try:
            # 获取所有元数据
            results = self.collection.get(include=["metadatas"])
            
            # 按文档ID分组
            documents = {}
            for metadata in results['metadatas']:
                doc_id = metadata['document_id']
                if doc_id not in documents:
                    documents[doc_id] = {
                        "id": doc_id,
                        "filename": metadata['filename'],
                        "chunk_count": metadata['chunk_count']
                    }
            
            return list(documents.values())
            
        except Exception as e:
            raise Exception(f"获取文档列表失败: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        if self.mode == "simple":
            return self.simple_kb.get_stats()
        
        try:
            count = self.collection.count()
            documents = self.list_documents()
            
            return {
                "total_chunks": count,
                "total_documents": len(documents),
                "documents": documents
            }
            
        except Exception as e:
            raise Exception(f"获取统计信息失败: {str(e)}") 