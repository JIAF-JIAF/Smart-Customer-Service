"""DOCX文件加载器"""

from typing import List, Dict
from modules.store.loaders.base import BaseLoader
from modules.store.vector_store import VectorStore


class DOCXLoader(BaseLoader):
    """DOCX文件加载器"""
    
    extensions = [".docx"]
    
    def load(self, file_path: str) -> List[Dict]:
        """加载DOCX文件
        
        参数:
            file_path: 文件路径
            
        返回:
            文档内容列表
        """
        try:
            import docx
            doc = docx.Document(file_path)
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return [{"page_content": content, "metadata": {"source": file_path}}]
        except Exception as e:
            print(f"读取DOCX文件失败: {e}")
            return []


