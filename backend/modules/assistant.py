"""
助手模块
负责初始化和管理 AI 助手
"""

import json
import os
from openai import OpenAI
from modules.plugins import tool_registry
from modules.context import ContextManager


class Assistant:
    """AI 助手管理类"""
    
    def __init__(self, config_path="config.json"):
        """初始化助手"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.client = None
        self.model = self.config.get('model', 'qwen3.6-flash')
        
        # 加载助手指令
        assistant_config_path = self.config.get('assistant_config_path', 'assistant.json')
        with open(assistant_config_path, 'r', encoding='utf-8') as f:
            assistant_config = json.load(f)
        
        self.instructions = assistant_config.get('instructions', '')
        # 使用注册表中的工具定义，而不是从配置文件加载
        self.tools_definition = tool_registry.get_all_definitions()
        
        # 初始化上下文管理器
        self.context_manager = ContextManager()
    
    def init_client(self):
        """初始化 OpenAI 客户端(阿里云百炼)"""
        self.client = OpenAI(
            api_key=self.config['api_key'],
            base_url=self.config['base_url']
        )
        print("API 客户端初始化成功")
        return self.client
    
    def get_or_create_session(self, session_id):
        """获取或创建会话"""
        return self.context_manager.get_or_create_session(session_id, self.instructions)
    
    def chat(self, session_id, user_message):
        """
        发送对话消息
        
        参数:
            session_id: 会话 ID
            user_message: 用户消息
        
        返回:
            dict: 包含回复内容和工具调用信息
        """
        if not self.client:
            raise Exception("请先初始化客户端")
        
        # 获取会话历史
        messages = self.get_or_create_session(session_id)
        
        # 添加用户消息
        self.context_manager.add_message(session_id, {
            "role": "user", 
            "content": user_message
        })
        
        # 调用 API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools_definition if self.tools_definition else None,
            tool_choice="auto"
        )
        
        # 获取助手回复
        choice = response.choices[0]
        assistant_message = choice.message
        
        # 添加入历史记录（tool_calls 保存完整的 API 响应，便于调试和追溯）
        self.context_manager.add_message(session_id, {
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": assistant_message.tool_calls
        })
        
        # 检查是否有工具调用
        tool_calls = []
        if assistant_message.tool_calls:
            for tc in assistant_message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments)
                })
        
        # 修剪会话历史，避免过长
        self.context_manager.prune_session_history(session_id)
        
        return {
            "content": assistant_message.content or "",
            "tool_calls": tool_calls
        }
    
    def submit_tool_result(self, session_id, tool_call_id, tool_result):
        """
        提交工具执行结果
        
        参数:
            session_id: 会话 ID
            tool_call_id: 工具调用 ID
            tool_result: 工具执行结果
        """
        messages = self.context_manager.get_session_history(session_id)
        
        # 添加工具结果
        self.context_manager.add_message(session_id, {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(tool_result, ensure_ascii=False)
        })
        
        # 继续对话
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools_definition if self.tools_definition else None
        )
        
        # 获取最终回复
        choice = response.choices[0]
        assistant_message = choice.message
        
        # 添加助手回复到历史记录
        assistant_msg = {
            "role": "assistant",
            "content": assistant_message.content or ""
        }
        self.context_manager.add_message(session_id, assistant_msg)
        
        # 修剪会话历史，避免过长
        self.context_manager.prune_session_history(session_id)
        
        return assistant_message.content or ""


# 全局实例
_assistant = None

def get_assistant():
    """获取助手单例"""
    global _assistant
    if _assistant is None:
        _assistant = Assistant()
        _assistant.init_client()
    return _assistant