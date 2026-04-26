"""
上下文管理模块
负责管理对话上下文和会话历史
"""

import json
from typing import List, Dict, Optional, Any


class Memory:
    """记忆管理器"""
    
    def __init__(self):
        """初始化记忆管理器"""
        # 会话历史存储 {session_id: [messages]}
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
    
    def get_or_create_session(self, session_id: str, system_instructions: str = "") -> List[Dict[str, Any]]:
        """
        获取或创建会话
        
        参数:
            session_id: 会话 ID
            system_instructions: 系统指令
            
        返回:
            会话历史列表
        """
        if session_id not in self.sessions:
            # 初始化会话,包含系统指令
            self.sessions[session_id] = []

            if system_instructions:
                self.sessions[session_id].append({"role": "system", "content": system_instructions})

        return self.sessions[session_id]
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """
        添加消息到会话历史
        
        参数:
            session_id: 会话 ID
            message: 消息对象
        """
        if session_id in self.sessions:
            self.sessions[session_id].append(message)
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话历史
        
        参数:
            session_id: 会话 ID
            
        返回:
            会话历史列表
        """
        return self.sessions.get(session_id, [])
    
    def clear_session(self, session_id: str) -> None:
        """
        清除会话历史
        
        参数:
            session_id: 会话 ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_all_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有会话
        
        返回:
            所有会话历史
        """
        return self.sessions
    
    def update_session(self, session_id: str, messages: List[Dict[str, Any]]) -> None:
        """
        更新会话历史
        
        参数:
            session_id: 会话 ID
            messages: 新的会话历史
        """
        self.sessions[session_id] = messages
    
    def prune_session_history(self, session_id: str, max_messages: int = 50) -> None:
        """
        修剪会话历史，保持在指定长度内
        
        参数:
            session_id: 会话 ID
            max_messages: 最大消息数
        """
        if session_id in self.sessions:
            # 保留系统消息，修剪其他消息
            system_messages = [msg for msg in self.sessions[session_id] if msg.get('role') == 'system']
            other_messages = [msg for msg in self.sessions[session_id] if msg.get('role') != 'system']
            
            # 确保至少保留系统消息和最近的一些消息
            if len(system_messages) + len(other_messages) > max_messages:
                # 保留系统消息和最近的消息
                self.sessions[session_id] = system_messages + other_messages[-(max_messages - len(system_messages)):]
