"""
工具插件基类
定义工具插件的基本结构和接口
"""


class ToolPlugin:
    """工具插件基类"""
    def __init__(self, name, definition, handler):
        self.name = name
        self.definition = definition
        self.handler = handler
    
    def execute(self, args):
        """执行工具"""
        return self.handler(args)
