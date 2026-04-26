"""
向量存储模块
负责文档向量化和知识库管理
"""

import os
import json
from typing import List, Dict, Optional


class VectorStore:
    """向量存储管理类"""

    def __init__(self, ai_client):
        """初始化向量存储

        参数:
            ai_client: AI 客户端实例
        """
        self.vector_store = None
        self.ai_client = ai_client
        self.knowledge_base = "knowledge_base"
        self.chroma_db = "chroma_db"
    
    def init_embeddings(self):
        """初始化嵌入模型"""
        # 直接使用传入的 AI 客户端
        if not self.ai_client:
            raise ValueError("AI 客户端未提供")
        return self.ai_client
    
    def load_document(self, file_path: str):
        """加载文档
        
        参数:
            file_path: 文件路径
            
        返回:
            文档内容列表
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".txt":
            try:
                with open(file_path, 'r', encoding="utf-8") as f:
                    content = f.read()
                return [{"page_content": content, "metadata": {"source": file_path}}]
            except Exception as e:
                print(f"读取文本文件失败: {e}")
                return []
        elif ext == ".pdf":
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
        elif ext == ".docx":
            try:
                import docx
                doc = docx.Document(file_path)
                content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                return [{"page_content": content, "metadata": {"source": file_path}}]
            except Exception as e:
                print(f"读取DOCX文件失败: {e}")
                return []
        else:
            print(f"不支持的文件格式: {ext}")
            return []
    
    def split_document(self, documents, chunk_size=500, chunk_overlap=50):
        """分割文档
        
        参数:
            documents: 文档对象列表
            chunk_size:  chunk 大小
            chunk_overlap:  chunk 重叠大小
            
        返回:
            分割后的文档
        """
        chunks = []
        for doc in documents:
            content = doc["page_content"]
            if not content:
                continue
            
            # 简单的文档分割
            words = content.split()
            for i in range(0, len(words), chunk_size - chunk_overlap):
                chunk_words = words[i:i + chunk_size]
                chunk = " ".join(chunk_words)
                chunks.append({"page_content": chunk, "metadata": doc["metadata"]})
        return chunks
    
    def create_vector_store(self, splits):
        """创建向量存储
        
        参数:
            splits: 分割后的文档
            
        返回:
            向量存储数据
        """
        if not self.ai_client:
            self.init_embeddings()
        
        # 确保 chroma_db 目录存在
        os.makedirs(self.chroma_db, exist_ok=True)
        
        # 简单的向量存储实现
        vector_data = []
        for split in splits:
            embedding = self.ai_client.create_embedding(split["page_content"])
            if embedding:
                vector_data.append({
                    "text": split["page_content"],
                    "embedding": embedding,
                    "metadata": split["metadata"]
                })
        
        # 保存向量数据
        with open(os.path.join(self.chroma_db, "vector_data.json"), 'w', encoding="utf-8") as f:
            json.dump(vector_data, f, ensure_ascii=False, indent=2)
        
        self.vector_store = vector_data
        return vector_data
    
    def load_knowledge_base(self):
        """加载知识库
        
        返回:
            向量存储数据
        """
        if not self.ai_client:
            self.init_embeddings()
        
        vector_data_path = os.path.join(self.chroma_db, "vector_data.json")
        if os.path.exists(vector_data_path):
            try:
                with open(vector_data_path, 'r', encoding="utf-8") as f:
                    vector_data = json.load(f)
                self.vector_store = vector_data
                return vector_data
            except Exception as e:
                print(f"加载向量存储失败: {e}")
                return None
        return None
    
    def search_similar(self, query: str, k=3):
        """搜索相似文档
        
        参数:
            query: 查询文本
            k: 返回结果数量
            
        返回:
            相似文档列表
        """
        if not self.vector_store:
            self.load_knowledge_base()
        
        if not self.vector_store:
            return []
        
        try:
            # 计算查询向量
            query_embedding = self.ai_client.create_embedding(query)
            if not query_embedding:
                return []
            
            # 计算相似度
            import numpy as np
            results = []
            for item in self.vector_store:
                similarity = np.dot(query_embedding, item["embedding"]) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(item["embedding"])
                )
                results.append({
                    "text": item["text"],
                    "similarity": float(similarity),
                    "metadata": item["metadata"]
                })
            
            # 排序并返回
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:k]
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def create_embeddings(self, text: str):
        """创建文本嵌入
        
        参数:
            text: 文本
            
        返回:
            嵌入向量
        """
        if not self.ai_client:
            self.init_embeddings()
        
        try:
            return self.ai_client.create_embedding(text)
        except Exception as e:
            print(f"创建嵌入失败: {e}")
            return []
    
    def check_knowledge_base_exists(self):
        """检查知识库是否存在
        
        返回:
            bool: 知识库是否存在
        """
        return os.path.exists(os.path.join(self.chroma_db, "vector_data.json"))
    
    def init_knowledge_base(self):
        """初始化知识库
        
        返回:
            dict: 知识库信息
        """
        # 检查是否已有向量存储
        existing_vector_store = self.load_knowledge_base()
        if existing_vector_store:
            print("发现现有知识库，直接加载")
            return {
                "status": "existing",
                "message": "知识库已存在，直接加载",
                "entries": existing_vector_store
            }
        
        # 检查知识目录
        if not os.path.exists(self.knowledge_base):
            os.makedirs(self.knowledge_base, exist_ok=True)
            print(f"创建知识目录: {self.knowledge_base}")
            return {
                "status": "empty",
                "message": "知识目录为空，请添加文档"
            }
        
        # 加载文档
        documents = []
        for root, _, files in os.walk(self.knowledge_base):
            for file in files:
                if file.endswith((".txt", ".pdf", ".docx")):
                    file_path = os.path.join(root, file)
                    try:
                        docs = self.load_document(file_path)
                        documents.extend(docs)
                        print(f"加载文档: {file_path}")
                    except Exception as e:
                        print(f"加载文档失败 {file_path}: {e}")
        
        if not documents:
            print("知识目录中没有可加载的文档")
            return {
                "status": "empty",
                "message": "知识目录中没有可加载的文档"
            }
        
        # 分割文档
        splits = self.split_document(documents)
        print(f"分割文档完成，共 {len(splits)} 个 chunk")
        
        # 创建向量存储
        vector_data = self.create_vector_store(splits)
        print("知识库初始化完成")
        
        return {
            "status": "created",
            "message": "知识库初始化完成",
            "document_count": len(documents),
            "chunk_count": len(splits),
            "entries": vector_data
        }
