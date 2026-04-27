"""PDF文件加载器"""

from typing import List, Dict
from modules.store.loaders.base import BaseLoader
from modules.store.vector_store import VectorStore


class PDFLoader(BaseLoader):
    """PDF文件加载器"""
    
    extensions = [".pdf"]
    
    def load(self, file_path: str) -> List[Dict]:
        """加载PDF文件
        
        参数:
            file_path: 文件路径
            
        返回:
            文档内容列表
        """
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pages = []
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    pages.append({"page_content": page.extract_text(), "metadata": {"source": file_path, "page": page_num + 1}})
                return pages
        except Exception as e:
            print(f"读取PDF文件失败: {e}")
            return []


