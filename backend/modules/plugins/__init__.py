"""
工具插件包
每个工具都是独立的插件文件,在导入时自动注册
"""

from .base import ToolPlugin, ToolRegistry, tool_registry

# 导入所有工具插件以触发自动注册
from ..tools import submit_form_plugin
from ..tools import weather_plugin

__all__ = ['ToolPlugin', 'ToolRegistry', 'tool_registry']