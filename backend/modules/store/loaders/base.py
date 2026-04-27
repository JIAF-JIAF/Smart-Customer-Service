"""基础加载器类"""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLoader(ABC):
    """加载器基类"""
    
    # 类属性：支持的文件扩展名
    extensions = []
    
    @abstractmethod
    def load(self, file_path: str) -> List[Dict]:
        """加载文档
        
        参数:
            file_path: 文件路径
            
        返回:
            文档内容列表
        """
        pass
    
    @classmethod
    def get_extensions(cls) -> List[str]:
        """获取支持的文件扩展名"""
        return cls.extensions