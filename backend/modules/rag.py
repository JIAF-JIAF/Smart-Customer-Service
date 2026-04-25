"""
RAG 模块
检索增强生成 - 从知识库中检索相关内容
"""

import numpy as np
from typing import List, Dict, Optional, Callable


class RAG:
    """简单的 RAG 检索器"""

    def __init__(self, knowledge_base: Optional[Dict] = None):
        """初始化 RAG 模块

        参数:
            knowledge_base: 知识库数据，包含 entries 列表
        """
        self.knowledge_base = knowledge_base

    def set_knowledge_base(self, knowledge_base: Dict) -> None:
        """设置知识库"""
        self.knowledge_base = knowledge_base

    def compute_similarity(self, vec1: list, vec2: list) -> float:
        """计算两个向量的余弦相似度"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def retrieve(self, query_embedding: list, top_k: int = 3) -> List[Dict]:
        """检索与查询最相关的知识库条目

        参数:
            query_embedding: 查询文本的向量
            top_k: 返回的结果数量

        返回:
            检索结果列表，每项包含 text 和 similarity
        """
        if not self.knowledge_base or not self.knowledge_base.get('entries'):
            return []

        results = []
        for entry in self.knowledge_base['entries']:
            similarity = self.compute_similarity(query_embedding, entry['embedding'])
            results.append({
                'text': entry['text'],
                'similarity': float(similarity)
            })

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    def build_context(self, query_embedding: list, top_k: int = 3) -> str:
        """构建检索上下文

        参数:
            query_embedding: 查询文本的向量
            top_k: 用于构建上下文的条目数量

        返回:
            格式化的上下文字符串
        """
        results = self.retrieve(query_embedding, top_k)

        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result['text']}")

        return "\n\n".join(context_parts)

    def enhance_query(self, query: str, embed_func: Callable[[str], Optional[list]], top_k: int = 3) -> str:
        """增强用户查询，将检索到的相关知识拼接到查询中

        参数:
            query: 用户原始查询文本
            embed_func: 生成向量嵌入的函数，接收文本返回向量
            top_k: 用于增强的检索条目数量

        返回:
            增强后的查询文本，如果无相关知识则返回原始查询
        """
        if not self.knowledge_base:
            return query

        query_embedding = embed_func(query)
        if not query_embedding:
            return query

        context = self.build_context(query_embedding, top_k)
        if not context:
            return query

        return "【相关知识】\n{}\n\n【用户问题】\n{}".format(context, query)


_rag = None


def get_rag(knowledge_base: Optional[Dict] = None) -> RAG:
    """获取 RAG 单例"""
    global _rag
    if _rag is None:
        _rag = RAG(knowledge_base)
    elif knowledge_base is not None:
        _rag.set_knowledge_base(knowledge_base)
    return _rag
