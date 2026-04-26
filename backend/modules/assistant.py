"""
助手模块
负责初始化和管理 AI 助手
"""

import json
from openai import OpenAI
from modules.context import ContextManager


class Assistant:
    """AI 助手管理类"""
    
    def __init__(self, config_path="config.json", options=None):
        """初始化助手
        
        参数:
            config_path: 配置文件路径
            options: 配置选项对象
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.client = None
        self.model = self.config.get('model', 'qwen3.6-flash')
        
        # 加载助手指令
        assistant_config_path = self.config.get('assistant_config_path', 'assistant.json')
        with open(assistant_config_path, 'r', encoding='utf-8') as f:
            assistant_config = json.load(f)
        
        self.instructions = assistant_config.get('instructions', '')
        
        # 初始化工具相关
        self.tools = []  # 工具实例列表
        self.tools_definition = []  # 工具定义列表
        self.tool_map = {}  # 工具名称到实例的映射
        
        # 初始化上下文管理器
        self.context_manager = ContextManager()
        
        # 模块管理
        self.rag_module = None
        self.vector_store = None
        
        # 处理选项
        if options:
            if 'rag_module' in options:
                self.rag_module = options['rag_module']
            if 'vector_store' in options:
                self.vector_store = options['vector_store']
            if 'tools' in options:
                self.set_tools(options['tools'])
    
    def set_rag_module(self, rag_module, vector_store=None):
        """设置 RAG 模块
        
        参数:
            rag_module: RAG 模块实例
            vector_store: 向量存储实例（用于生成嵌入）
        """
        self.rag_module = rag_module
        self.vector_store = vector_store
    
    def set_tools(self, tools):
        """设置工具实例
        
        参数:
            tools: 工具实例列表，每个实例应包含 name、definition 和 execute 方法
        """
        self.tools = tools
        self.tools_definition = [tool.definition for tool in tools]
        self.tool_map = {tool.name: tool for tool in tools}
        
        # 注册工具
        for tool in tools:
            print(f"工具注册成功: {tool.name}")
    
    def enhance_query(self, user_message):
        """使用 RAG 增强查询
        
        参数:
            user_message: 用户原始消息
            
        返回:
            增强后的消息
        """
        if self.rag_module and self.vector_store:
            try:
                return self.rag_module.enhance_query(
                    user_message,
                    self.vector_store.create_embeddings,
                    top_k=3
                )
            except Exception as e:
                print("RAG 检索失败: {}".format(e))
                return user_message
        return user_message
    
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
        self.context_manager.add_message(session_id, {
            "role": "assistant",
            "content": assistant_message.content or ""
        })
        
        # 修剪会话历史，避免过长
        self.context_manager.prune_session_history(session_id)
        
        return assistant_message.content or ""
    
    def process_message(self, session_id, user_message):
        """
        处理完整的对话流程
        
        参数:
            session_id: 会话 ID
            user_message: 用户消息
            
        返回:
            dict: 包含回复内容和工具调用信息
        """
        # 1. RAG 增强查询
        enhanced_message = self.enhance_query(user_message)
        
        # 2. 调用助手对话
        result = self.chat(session_id, enhanced_message)
        
        # 3. 检查是否需要调用工具
        if result['tool_calls']:
            print("检测到 {} 个工具调用".format(len(result['tool_calls'])))

            for tool_call in result['tool_calls']:
                tool_name = tool_call['name']
                tool_args = tool_call['arguments']
                tool_call_id = tool_call['id']

                print("调用工具: {}".format(tool_name))
                print("参数: {}".format(tool_args))

                # 执行工具
                if tool_name in self.tool_map:
                    tool = self.tool_map[tool_name]
                    tool_result = tool.execute(tool_args)
                    print("工具执行结果: {}".format(tool_result))
                else:
                    tool_result = {
                        "success": False,
                        "message": "未知工具: {}".format(tool_name)
                    }
                    print("工具执行失败: 未知工具 {}".format(tool_name))
                
                # 提交工具结果并获取最终回复
                final_reply = self.submit_tool_result(
                    session_id, 
                    tool_call_id, 
                    tool_result
                )
                
                print("AI: {}".format(final_reply))
                
                return {
                    "reply": final_reply,
                    "tool_calls": [tool_call],
                    "session_id": session_id,
                    "finished": False
                }
        
        # 4. 无工具调用,直接返回
        print("AI: {}".format(result['content']))
        
        return {
            "reply": result['content'],
            "tool_calls": [],
            "session_id": session_id,
            "finished": False
        }


# 全局实例
_assistant = None

def get_assistant(options=None):
    """获取助手单例
    
    参数:
        options: 配置选项对象
            - rag_module: RAG 模块实例（可选）
            - vector_store: 向量存储实例（可选）
            - tools: 工具定义列表（可选）
    """
    global _assistant
    if _assistant is None:
        _assistant = Assistant(options=options)
        _assistant.init_client()
    else:
        # 如果提供了选项，更新配置
        if options:
            if 'rag_module' in options:
                _assistant.set_rag_module(options['rag_module'], options.get('vector_store'))
            if 'tools' in options:
                _assistant.set_tools(options['tools'])
    
    return _assistant