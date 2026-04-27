"""加载器模块包"""

from modules.store.loaders.base import BaseLoader
from modules.store.loaders.txt_loader import TXTLoader
from modules.store.loaders.pdf_loader import PDFLoader
from modules.store.loaders.docx_loader import DOCXLoader

__all__ = ['BaseLoader', 'TXTLoader', 'PDFLoader', 'DOCXLoader']