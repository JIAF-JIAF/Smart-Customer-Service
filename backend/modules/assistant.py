"""
助手模块
负责初始化和管理 AI 助手
"""

import json
from openai import OpenAI
from modules.context import Memory


class Assistant:
    """AI 助手管理类"""

    def __init__(self, config_path="config.json", options=None):
        """初始化助手

        参数:
            config_path: 配置文件路径
            options: 配置选项对象，可包含:
                - ragModule: RAG 模块实例
                - vectorStore: 向量存储实例
                - tools: 工具定义列表
                - prompt: prompt 字符串（可选）
                - aiClient: AI 客户端实例（可选）
                - memory: 记忆管理器实例（可选）
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.client = None
        self.ai_client = None
        self.model = self.config.get('model', 'qwen3.6-flash')

        if options and 'prompt' in options:
            self.prompt = options['prompt']
        else:
            self.prompt = None
        
        # 初始化工具相关
        self.tools = []  # 工具实例列表
        self.tools_definition = []  # 工具定义列表
        self.tool_map = {}  # 工具名称到实例的映射
        
        # 模块管理
        self.ragModule = None
        self.vectorStore = None
        
        # 初始化记忆管理器
        if options and 'memory' in options:
            self.memory = options['memory']
        else:
            self.memory = Memory()
        
        # 处理其他选项
        if options:
            if 'ragModule' in options:
                self.ragModule = options['ragModule']
            if 'vectorStore' in options:
                self.vectorStore = options['vectorStore']
            if 'tools' in options:
                self.set_tools(options['tools'])
            if 'aiClient' in options:
                self.ai_client = options['aiClient']
    
    def set_rag_module(self, ragModule, vectorStore=None):
        """设置 RAG 模块

        参数:
            ragModule: RAG 模块实例
            vectorStore: 向量存储实例（用于生成嵌入）
        """
        self.ragModule = ragModule
        self.vectorStore = vectorStore
    
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
        if self.ragModule and self.vectorStore:
            try:
                return self.ragModule.enhance_query(
                    user_message,
                    self.vectorStore.create_embeddings,
                    top_k=3
                )
            except Exception as e:
                print("RAG 检索失败: {}".format(e))
                return user_message
        return user_message
    
    def init_client(self):
        """初始化 OpenAI 客户端(阿里云百炼)"""
        if self.ai_client:
            self.client = self.ai_client.get_client()
            print("使用传入的 AI 客户端")
        else:
            # 保持向后兼容，从配置文件读取
            self.client = OpenAI(
                api_key=self.config['api_key'],
                base_url=self.config['base_url']
            )
            print("API 客户端初始化成功")
        return self.client
    
    def get_session(self, session_id):
        """获取会话"""
        return self.memory.get_session(session_id)

    def create_session(self, session_id):
        """创建会话"""
        system_content = self.prompt.format()["content"] if self.prompt else ""
        return self.memory.create_session(session_id, system_content)

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

        # 获取或创建会话
        messages = self.get_session(session_id)
        if messages is None:
            messages = self.create_session(session_id)

        # 添加用户消息
        if user_message:
            self.memory.add_message(session_id, {"role": "user", "content": user_message})

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
        self.memory.add_message(session_id, {
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
        self.memory.prune_session_history(session_id)

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
        # 添加工具结果
        self.memory.add_message(session_id, {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(tool_result, ensure_ascii=False)
        })

        # 继续对话
        messages = self.memory.get_session_history(session_id)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools_definition if self.tools_definition else None
        )

        # 获取最终回复
        choice = response.choices[0]
        assistant_message = choice.message

        # 添加助手回复到历史记录
        self.memory.add_message(session_id, {
            "role": "assistant",
            "content": assistant_message.content or ""
        })

        # 修剪会话历史，避免过长
        self.memory.prune_session_history(session_id)

        return assistant_message.content or ""
    
    def process_message(self, session_id, user_message):
        """
        处理完整的对话流程，支持多步骤链式工具调用
        
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
        
        # 3. 循环处理工具调用（支持链式调用）
        while result['tool_calls']:
            print("检测到 {} 个工具调用".format(len(result['tool_calls'])))

            # 执行所有工具调用（按顺序）
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
                
                # 提交工具结果到会话历史
                self.memory.add_message(session_id, {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # 继续对话，检查是否需要更多工具调用
            messages = self.memory.get_session_history(session_id)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools_definition if self.tools_definition else None,
                tool_choice="auto"
            )
            
            choice = response.choices[0]
            assistant_message = choice.message
            
            # 更新历史记录
            self.memory.add_message(session_id, {
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": assistant_message.tool_calls
            })
            
            # 检查是否还有工具调用
            tool_calls = []
            if assistant_message.tool_calls:
                for tc in assistant_message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    })
            
            result = {
                "content": assistant_message.content or "",
                "tool_calls": tool_calls
            }
            
            # 修剪会话历史
            self.memory.prune_session_history(session_id)
        
        # 4. 无工具调用,直接返回
        print("AI: {}".format(result['content']))
        
        return {
            "reply": result['content'],
            "tool_calls": [],
            "session_id": session_id,
            "finished": True
        }
