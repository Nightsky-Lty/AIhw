"""
文件夹监控服务 - 自动构建知识库
"""
import os
import time
import threading
from typing import Dict, Set, Callable, Optional
from pathlib import Path
import hashlib
from models.knowledge_base import KnowledgeBase
import config

class FolderWatcher:
    """文件夹监控器 - 自动构建知识库"""
    
    def __init__(self, knowledge_base: KnowledgeBase, watch_folder: str = "./uploads", auto_start: bool = True):
        self.kb = knowledge_base
        self.watch_folder = Path(watch_folder)
        self.file_hashes: Dict[str, str] = {}  # 文件路径 -> 文件哈希
        self.document_mapping: Dict[str, str] = {}  # 文件路径 -> 文档ID
        self.is_running = False
        self.watch_thread: Optional[threading.Thread] = None
        self.check_interval = 2  # 检查间隔（秒）
        
        # 确保监控文件夹存在
        self.watch_folder.mkdir(exist_ok=True)
        print(f"📁 文件夹监控器初始化完成，监控目录: {self.watch_folder.absolute()}")
        
        # 自动启动监控
        if auto_start:
            self.start_watching()
    
    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception:
            return ""
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """检查是否为支持的文件类型"""
        return file_path.suffix.lower() in config.SUPPORTED_EXTENSIONS
    
    def _scan_folder(self) -> Set[Path]:
        """扫描文件夹，返回所有支持的文件"""
        files = set()
        try:
            for file_path in self.watch_folder.rglob("*"):
                if file_path.is_file() and self._is_supported_file(file_path):
                    files.add(file_path)
        except Exception as e:
            print(f"❌ 扫描文件夹失败: {e}")
        return files
    
    def _add_file_to_kb(self, file_path: Path) -> bool:
        """添加文件到知识库"""
        try:
            doc_id = self.kb.add_document(str(file_path), file_path.name)
            self.document_mapping[str(file_path)] = doc_id
            self.file_hashes[str(file_path)] = self._get_file_hash(file_path)
            print(f"✅ 已添加文件到知识库: {file_path.name}")
            return True
        except Exception as e:
            print(f"❌ 添加文件失败 {file_path.name}: {e}")
            return False
    
    def _remove_file_from_kb(self, file_path: str) -> bool:
        """从知识库中删除文件"""
        try:
            if file_path in self.document_mapping:
                doc_id = self.document_mapping[file_path]
                success = self.kb.delete_document(doc_id)
                if success:
                    del self.document_mapping[file_path]
                    del self.file_hashes[file_path]
                    print(f"🗑️ 已从知识库删除文件: {Path(file_path).name}")
                    return True
            return False
        except Exception as e:
            print(f"❌ 删除文件失败 {Path(file_path).name}: {e}")
            return False
    
    def _update_file_in_kb(self, file_path: Path) -> bool:
        """更新知识库中的文件"""
        try:
            # 先删除旧版本
            if str(file_path) in self.document_mapping:
                self._remove_file_from_kb(str(file_path))
            
            # 添加新版本
            return self._add_file_to_kb(file_path)
        except Exception as e:
            print(f"❌ 更新文件失败 {file_path.name}: {e}")
            return False
    
    def _watch_loop(self):
        """监控循环"""
        print("🔍 开始监控文件夹变化...")
        
        while self.is_running:
            try:
                current_files = self._scan_folder()
                current_file_paths = {str(f) for f in current_files}
                known_file_paths = set(self.file_hashes.keys())
                
                # 检查新增文件
                new_files = current_file_paths - known_file_paths
                for file_path in new_files:
                    self._add_file_to_kb(Path(file_path))
                
                # 检查删除的文件
                deleted_files = known_file_paths - current_file_paths
                for file_path in deleted_files:
                    self._remove_file_from_kb(file_path)
                
                # 检查修改的文件
                for file_path in current_file_paths & known_file_paths:
                    current_hash = self._get_file_hash(Path(file_path))
                    if current_hash and current_hash != self.file_hashes.get(file_path):
                        self._update_file_in_kb(Path(file_path))
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ 监控循环出错: {e}")
                time.sleep(self.check_interval)
    
    def start_watching(self):
        """开始监控"""
        if self.is_running:
            print("⚠️ 文件夹监控已在运行中")
            return
        
        print(f"🚀 启动文件夹监控服务...")
        print(f"📂 监控目录: {self.watch_folder.absolute()}")
        print(f"📋 支持的文件类型: {', '.join(config.SUPPORTED_EXTENSIONS)}")
        
        # 初始扫描
        self._initial_scan()
        
        # 启动监控线程
        self.is_running = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
        
        print("✅ 文件夹监控服务已启动")
    
    def stop_watching(self):
        """停止监控"""
        if not self.is_running:
            print("⚠️ 文件夹监控已经停止")
            return
        
        print("🛑 停止文件夹监控服务...")
        self.is_running = False
        
        if self.watch_thread and self.watch_thread.is_alive():
            self.watch_thread.join(timeout=5)
        
        print("✅ 文件夹监控服务已停止")
    
    def _initial_scan(self):
        """初始扫描，添加现有文件"""
        print("🔄 执行初始文件扫描...")
        files = self._scan_folder()
        
        if not files:
            print("📝 监控文件夹为空，请将文档文件放入以下目录：")
            print(f"   {self.watch_folder.absolute()}")
            print("   支持的文件格式: " + ", ".join(config.SUPPORTED_EXTENSIONS))
            return
        
        success_count = 0
        for file_path in files:
            if self._add_file_to_kb(file_path):
                success_count += 1
        
        print(f"📊 初始扫描完成，成功添加 {success_count}/{len(files)} 个文件")
    
    def get_status(self) -> Dict:
        """获取监控状态"""
        return {
            "is_running": self.is_running,
            "watch_folder": str(self.watch_folder.absolute()),
            "tracked_files": len(self.file_hashes),
            "supported_extensions": config.SUPPORTED_EXTENSIONS,
            "files": [
                {
                    "path": path,
                    "name": Path(path).name,
                    "document_id": self.document_mapping.get(path)
                }
                for path in self.file_hashes.keys()
            ]
        }
    
    def force_rescan(self):
        """强制重新扫描"""
        print("🔄 执行强制重新扫描...")
        # 清空现有映射
        old_files = list(self.file_hashes.keys())
        for file_path in old_files:
            self._remove_file_from_kb(file_path)
        
        # 重新扫描
        self._initial_scan()
        print("✅ 强制重新扫描完成") 