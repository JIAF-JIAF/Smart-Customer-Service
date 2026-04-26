"""
AI 客户端模块
负责管理 OpenAI API 客户端
"""

import os
from openai import OpenAI


class AIClient:
    """AI 客户端管理类"""

    def __init__(self, api_key=None, base_url=None, config_path=None):
        """初始化 AI 客户端

        参数:
            api_key: OpenAI API 密钥
            base_url: OpenAI API 基础 URL
            config_path: 配置文件路径
        """
        # 优先使用传入的参数
        if api_key and base_url:
            pass
        # 其次从配置文件读取
        elif config_path:
            try:
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                api_key = config.get('api_key')
                base_url = config.get('base_url')
                print(f"从配置文件 {config_path} 读取 API 配置")
            except Exception as e:
                print(f"读取配置文件失败: {e}")
        
        if not api_key or not base_url:
            raise ValueError("请设置 OPENAI_API_KEY 和 OPENAI_API_BASE 环境变量或提供配置文件")
        
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        print("AI 客户端初始化成功")
    
    def get_client(self):
        """获取 OpenAI 客户端实例"""
        return self.client
    
    def create_embedding(self, text):
        """创建文本嵌入

        参数:
            text: 文本
            
        返回:
            嵌入向量
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-v3"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"生成嵌入失败: {e}")
            return []
