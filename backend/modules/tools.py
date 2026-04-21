"""
工具模块
定义可供 AI 调用的工具函数
"""

import json
from modules.airtable_api import submit_form


# 工具定义(与 assistant.json 保持一致)
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "submit_form",
            "description": "提交客户咨询表单,记录客户信息和咨询内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "客户姓名"
                    },
                    "phone": {
                        "type": "string",
                        "description": "客户联系电话"
                    },
                    "wechat": {
                        "type": "string",
                        "description": "客户微信号(可选)"
                    },
                    "address": {
                        "type": "string",
                        "description": "客户地址(可选)"
                    },
                    "intention": {
                        "type": "string",
                        "description": "客户咨询意图或需求概述"
                    }
                },
                "required": ["name", "phone", "intention"]
            }
        }
    }
]


def execute_tool(tool_name, arguments):
    """
    执行工具函数
    
    参数:
        tool_name: 工具名称
        arguments: 工具参数(dict)
    
    返回:
        dict: 工具执行结果
    """
    try:
        if tool_name == "submit_form":
            return _handle_submit_form(arguments)
        else:
            return {
                "success": False,
                "message": f"未知工具: {tool_name}"
            }
    except Exception as e:
        print(f"工具执行异常: {e}")
        return {
            "success": False,
            "message": f"工具执行异常: {str(e)}"
        }


def _handle_submit_form(arguments):
    """处理表单提交"""
    # 提取参数
    name = arguments.get('name', '')
    phone = arguments.get('phone', '')
    wechat = arguments.get('wechat')
    address = arguments.get('address')
    intention = arguments.get('intention', '')
    
    # 生成摘要(AI 已在对话中生成,这里可以调用 AI 或简单处理)
    summary = f"客户 {name} 咨询: {intention}"
    
    # 提交表单
    result = submit_form(
        name=name,
        phone=phone,
        wechat=wechat,
        address=address,
        summary=summary,
        intention=intention
    )
    
    return result


def get_tools_definition():
    """获取工具定义(用于初始化助手)"""
    return TOOLS_DEFINITION


def load_tools_from_config(config_path="assistant.json"):
    """从配置文件加载工具定义"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('tools', TOOLS_DEFINITION)
    except:
        return TOOLS_DEFINITION
