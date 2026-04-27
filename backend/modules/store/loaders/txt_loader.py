"""文本文件加载器"""

from typing import List, Dict
from modules.store.loaders.base import BaseLoader


class TXTLoader(BaseLoader):
    """文本文件加载器"""
    
    extensions = [".txt"]
    
    def load(self, file_path: str) -> List[Dict]:
        """加载文本文件
        
        参数:
            file_path: 文件路径
            
        返回:
            文档内容列表
        """
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                content = f.read()
            return [{"page_content": content, "metadata": {"source": file_path}}]
        except Exception as e:
            print(f"读取文本文件失败: {e}")
            return []


