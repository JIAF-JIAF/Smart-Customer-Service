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
            print("生成向量失败: {}".format(e))
            return None

    def load_raw_knowledge(self, file_path="data/raw_knowledge.txt"):
        """加载原始知识文本"""
        if not os.path.exists(file_path):
            print("知识文件不存在: {}".format(file_path))
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return paragraphs

    def save_knowledge_base(self, data):
        """保存知识库到 JSON"""
        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("知识库已保存到: {}".format(self.knowledge_base_path))

    def load_knowledge_base(self):
        """加载向量化数据"""
        if not os.path.exists(self.knowledge_base_path):
            return None

        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def init_knowledge_base(self):
        """初始化知识库"""
        if self.check_knowledge_base_exists():
            print("知识库已存在,跳过向量化")
            return self.load_knowledge_base()

        print("开始初始化知识库...")

        paragraphs = self.load_raw_knowledge()
        if not paragraphs:
            print("未找到知识内容,创建空知识库")
            empty_kb = {"entries": [], "version": "1.0"}
            self.save_knowledge_base(empty_kb)
            return empty_kb

        print("加载了 {} 段知识文本".format(len(paragraphs)))

        entries = []
        for i, paragraph in enumerate(paragraphs):
            print("正在向量化第 {}/{} 段...".format(i+1, len(paragraphs)))

            embedding = self.create_embeddings(paragraph)
            if embedding is None:
                print("第 {} 段向量化失败,跳过".format(i+1))
                continue

            entry_id = str(uuid.uuid4())

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

        kb = {
            "entries": entries,
            "version": "1.0",
            "total_entries": len(entries)
        }

        self.save_knowledge_base(kb)
        print("知识库初始化完成,共 {} 条记录".format(len(entries)))

        return kb


_vector_store = None


def get_vector_store():
    """获取向量存储单例"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
