"""
向量存储模块
负责文档向量化和知识库管理
"""

import os
import json
from typing import List, Dict, Optional


class VectorStore:
    """向量存储管理类"""
    
    # 类属性：存储所有加载器
    _document_loaders = {}

    def __init__(self, ai_client):
        """初始化向量存储

        参数:
            ai_client: AI 客户端实例
        """
        self.vector_store = None
        self.ai_client = ai_client
        self.knowledge_base = "knowledge_base"
        self.chroma_db = "db"
        self.document_loaders = VectorStore._document_loaders.copy()
    
    @classmethod
    def register_loader(cls, loader):
        """注册文档加载器（类方法）
        
        参数:
            loader: 加载器实例，继承自 BaseLoader
        """
        for ext in loader.get_extensions():
            cls._document_loaders[ext.lower()] = loader
            print(f"注册加载器: {loader.__class__.__name__} 支持 {ext}")

    def load_document(self, file_path: str):
        """加载文档
        
        参数:
            file_path: 文件路径
            
        返回:
            文档内容列表
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in self.document_loaders:
            return self.document_loaders[ext].load(file_path)
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
        
        # 只有当向量数据非空时才存储
        if vector_data:
            # 确保 db 目录存在
            os.makedirs(self.chroma_db, exist_ok=True)
            
            # 保存向量数据
            with open(os.path.join(self.chroma_db, "vector_data.json"), 'w', encoding="utf-8") as f:
                json.dump(vector_data, f, ensure_ascii=False, indent=2)
            
            self.vector_store = vector_data
            print(f"向量存储创建成功，共 {len(vector_data)} 个向量")
        else:
            print("向量存储创建失败：没有生成有效的向量数据")
            self.vector_store = None
        
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
                
                # 检查向量数据是否有效
                if vector_data and isinstance(vector_data, list):
                    self.vector_store = vector_data
                    print(f"加载知识库成功，共 {len(vector_data)} 个向量")
                    return vector_data
                else:
                    print("加载知识库失败：向量数据为空或格式无效")
                    self.vector_store = None
                    return None
            except Exception as e:
                print(f"加载向量存储失败: {e}")
                self.vector_store = None
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
    
    def get_vectorized_files(self):
        """获取已向量化的文件列表
        
        返回:
            set: 已向量化的文件路径集合
        """
        if not self.vector_store:
            self.load_knowledge_base()
        
        if not self.vector_store:
            return set()
        
        vectorized_files = set()
        for item in self.vector_store:
            if "metadata" in item and "source" in item["metadata"]:
                vectorized_files.add(item["metadata"]["source"])
        return vectorized_files
    
    def check_new_files(self):
        """检查知识库目录中的新文件
        
        返回:
            dict: 新文件信息
        """
        vectorized_files = self.get_vectorized_files()
        new_files = []
        existing_files = []
        
        if not os.path.exists(self.knowledge_base):
            return {
                "new_files": [],
                "existing_files": [],
                "message": "知识目录不存在"
            }
        
        for root, _, files in os.walk(self.knowledge_base):
            for file in files:
                if file.endswith((".txt", ".pdf", ".docx")):
                    file_path = os.path.join(root, file)
                    if file_path in vectorized_files:
                        existing_files.append(file_path)
                    else:
                        new_files.append(file_path)
        
        return {
            "new_files": new_files,
            "existing_files": existing_files,
            "new_count": len(new_files),
            "existing_count": len(existing_files)
        }
    
    def init_knowledge_base(self, incremental=True):
        """初始化知识库
        
        参数:
            incremental: 是否使用增量模式（默认True，仅向量化新文件）
            
        返回:
            dict: 知识库信息
        """
        existing_vector_store = self.load_knowledge_base()
        vectorized_files = self.get_vectorized_files() if incremental else set()
        
        if not os.path.exists(self.knowledge_base):
            os.makedirs(self.knowledge_base, exist_ok=True)
            print(f"创建知识目录: {self.knowledge_base}")
            return {
                "status": "empty",
                "message": "知识目录为空，请添加文档"
            }
        
        documents = []
        new_file_count = 0
        skipped_file_count = 0
        
        for root, _, files in os.walk(self.knowledge_base):
            for file in files:
                if file.endswith((".txt", ".pdf", ".docx")):
                    file_path = os.path.join(root, file)
                    if incremental and file_path in vectorized_files:
                        print(f"跳过已向量化的文件: {file_path}")
                        skipped_file_count += 1
                        continue
                    try:
                        docs = self.load_document(file_path)
                        if docs:
                            documents.extend(docs)
                            print(f"加载文档: {file_path}")
                            new_file_count += 1
                    except Exception as e:
                        print(f"加载文档失败 {file_path}: {e}")
        
        if not documents:
            print(f"没有新文档需要向量化（跳过 {skipped_file_count} 个已存在文件）")
            return {
                "status": "no_new_docs",
                "message": "没有新文档需要向量化",
                "skipped_count": skipped_file_count,
                "entries": existing_vector_store
            }
        
        splits = self.split_document(documents)
        print(f"分割文档完成，共 {len(splits)} 个 chunk")
        
        new_vector_data = self.create_vector_store(splits)
        
        if incremental and existing_vector_store and new_vector_data:
            merged_vectors = existing_vector_store + new_vector_data
            os.makedirs(self.chroma_db, exist_ok=True)
            with open(os.path.join(self.chroma_db, "vector_data.json"), 'w', encoding="utf-8") as f:
                json.dump(merged_vectors, f, ensure_ascii=False, indent=2)
            self.vector_store = merged_vectors
            print(f"知识库增量更新完成，新增 {len(new_vector_data)} 个向量，总计 {len(merged_vectors)} 个向量")
            return {
                "status": "incremental_updated",
                "message": "知识库增量更新完成",
                "new_document_count": new_file_count,
                "new_chunk_count": len(splits),
                "skipped_count": skipped_file_count,
                "total_entries": len(merged_vectors),
                "entries": merged_vectors
            }
        elif new_vector_data:
            print("知识库初始化完成")
            return {
                "status": "created",
                "message": "知识库初始化完成",
                "document_count": new_file_count,
                "chunk_count": len(splits),
                "entries": new_vector_data
            }
        else:
            print("知识库初始化失败：向量存储创建失败")
            return {
                "status": "failed",
                "message": "知识库初始化失败：向量存储创建失败"
            }

# 导入并注册文档加载器
# 注意：必须在 VectorStore 类定义之后导入，以避免循环导入
from modules.store.loaders import TXTLoader, PDFLoader, DOCXLoader

# 注册加载器
VectorStore.register_loader(TXTLoader())
VectorStore.register_loader(PDFLoader())
VectorStore.register_loader(DOCXLoader())