"""
向量化存储模块
负责知识库的向量化处理和存储管理
"""

import json
import os
import uuid
from openai import OpenAI


class VectorStore:
    """向量化存储管理类"""
    
    def __init__(self, config_path="config.json"):
        """初始化向量存储"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.knowledge_base_path = self.config.get('knowledge_base_path', 'knowledge_base.json')
        self.embedding_model = self.config.get('embedding_model', 'text-embedding-v3')
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.config['api_key'],
            base_url=self.config['base_url']
        )
    
    def check_knowledge_base_exists(self):
        """检查知识库是否已存在"""
        if not os.path.exists(self.knowledge_base_path):
            return False
        
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data.get('entries', [])) > 0
        except:
            return False
    
    def create_embeddings(self, text):
        """调用 API 生成向量"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"生成向量失败: {e}")
            return None
    
    def load_raw_knowledge(self, file_path="data/raw_knowledge.txt"):
        """加载原始知识文本"""
        if not os.path.exists(file_path):
            print(f"知识文件不存在: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按段落分割(可根据实际情况调整)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return paragraphs
    
    def save_knowledge_base(self, data):
        """保存知识库到 JSON"""
        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"知识库已保存到: {self.knowledge_base_path}")
    
    def load_knowledge_base(self):
        """加载向量化数据"""
        if not os.path.exists(self.knowledge_base_path):
            return None
        
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def init_knowledge_base(self):
        """初始化知识库流程: 检查 -> 向量化 -> 保存"""
        # 1. 检查是否已存在
        if self.check_knowledge_base_exists():
            print("✓ 知识库已存在,跳过向量化")
            return self.load_knowledge_base()
        
        print("开始初始化知识库...")
        
        # 2. 加载原始知识
        paragraphs = self.load_raw_knowledge()
        if not paragraphs:
            print("⚠ 未找到知识内容,创建空知识库")
            empty_kb = {"entries": [], "version": "1.0"}
            self.save_knowledge_base(empty_kb)
            return empty_kb
        
        print(f"✓ 加载了 {len(paragraphs)} 段知识文本")
        
        # 3. 向量化处理
        entries = []
        for i, paragraph in enumerate(paragraphs):
            print(f"正在向量化第 {i+1}/{len(paragraphs)} 段...")
            
            # 生成向量
            embedding = self.create_embeddings(paragraph)
            if embedding is None:
                print(f"⚠ 第 {i+1} 段向量化失败,跳过")
                continue
            
            # 生成唯一 ID
            entry_id = str(uuid.uuid4())
            
            # 构建条目
            entry = {
                "id": entry_id,
                "text": paragraph,
                "embedding": embedding,
                "metadata": {
                    "index": i,
                    "length": len(paragraph)
                }
            }
            entries.append(entry)
        
        # 4. 保存知识库
        knowledge_base = {
            "entries": entries,
            "version": "1.0",
            "total_entries": len(entries)
        }
        
        self.save_knowledge_base(knowledge_base)
        print(f"✓ 知识库初始化完成,共 {len(entries)} 条记录")
        
        return knowledge_base
    
    def search_similar(self, query, top_k=3):
        """搜索相似内容(简单实现:基于向量余弦相似度)"""
        kb = self.load_knowledge_base()
        if not kb or not kb.get('entries'):
            return []
        
        # 生成查询向量
        query_embedding = self.create_embeddings(query)
        if query_embedding is None:
            return []
        
        # 计算相似度
        import numpy as np
        
        results = []
        for entry in kb['entries']:
            # 余弦相似度
            vec1 = np.array(query_embedding)
            vec2 = np.array(entry['embedding'])
            
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            results.append({
                "id": entry['id'],
                "text": entry['text'],
                "similarity": float(similarity)
            })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:top_k]


# 全局实例
_vector_store = None

def get_vector_store():
    """获取向量存储单例"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
