"""
工具插件目录
包含所有具体的工具实现
"""

# 导入所有工具插件以触发自动注册
from . import weather_plugin
from . import submit_form_plugin

__all__ = []