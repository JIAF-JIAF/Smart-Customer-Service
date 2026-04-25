"""
工具插件基类
"""


class ToolPlugin:
    """工具插件基类"""
    
    def __init__(self, name, definition, handler):
        """
        初始化工具插件
        
        参数:
            name: 工具名称
            definition: 工具定义(符合 OpenAI Function Calling 格式)
            handler: 工具执行函数
        """
        self.name = name
        self.definition = definition
        self.handler = handler
    
    def execute(self, arguments):
        """执行工具"""
        return self.handler(arguments)


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools = {}
    
    def register(self, tool_plugin):
        """
        注册工具插件
        
        参数:
            tool_plugin: ToolPlugin 实例
        """
        self._tools[tool_plugin.name] = tool_plugin
        print("工具插件已注册: {}".format(tool_plugin.name))
    
    def execute(self, tool_name, arguments):
        """
        执行工具
        
        参数:
            tool_name: 工具名称
            arguments: 工具参数(dict)
        
        返回:
            dict: 工具执行结果
        """
        if tool_name not in self._tools:
            return {
                "success": False,
                "message": "未知工具: {}".format(tool_name)
            }
        
        try:
            return self._tools[tool_name].execute(arguments)
        except Exception as e:
            print("工具执行异常: {}".format(e))
            return {
                "success": False,
                "message": "工具执行异常: {}".format(str(e))
            }
    
    def get_all_definitions(self):
        """获取所有工具定义(用于传递给 AI)"""
        return [tool.definition for tool in self._tools.values()]
    
    def get_tool_names(self):
        """获取所有已注册的工具名称"""
        return list(self._tools.keys())


# 全局工具注册表实例
tool_registry = ToolRegistry()