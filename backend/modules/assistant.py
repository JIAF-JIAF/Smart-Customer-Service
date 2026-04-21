"""
助手模块
负责初始化和管理 AI 助手
"""

import json
import os
from openai import OpenAI
from modules.tools import load_tools_from_config


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
        self.tools_definition = assistant_config.get('tools', [])
        
        # 会话历史存储 {session_id: [messages]}
        self.sessions = {}
        
    def init_client(self):
        """初始化 OpenAI 客户端(阿里云百炼)"""
        self.client = OpenAI(
            api_key=self.config['api_key'],
            base_url=self.config['base_url']
        )
        print("✓ API 客户端初始化成功")
        return self.client
    
    def get_or_create_session(self, session_id):
        """获取或创建会话"""
        if session_id not in self.sessions:
            # 初始化会话,包含系统指令
            self.sessions[session_id] = [
                {"role": "system", "content": self.instructions}
            ]
        return self.sessions[session_id]
    
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
        messages.append({"role": "user", "content": user_message})
        
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
        
        # 添加入历史记录
        messages.append({
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
        messages = self.sessions.get(session_id, [])
        
        # 添加工具结果
        messages.append({
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
        
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or ""
        })
        
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
