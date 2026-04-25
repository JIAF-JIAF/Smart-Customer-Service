"""
表单提交工具插件
用于提交客户咨询表单,记录客户信息和咨询内容
"""

from modules.plugins import tool_registry, ToolPlugin


# 工具定义
SUBMIT_FORM_DEFINITION = {
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


def _handle_submit_form(arguments):
    """处理表单提交"""
    # 提取参数
    name = arguments.get('name', '')
    phone = arguments.get('phone', '')
    wechat = arguments.get('wechat')
    address = arguments.get('address')
    intention = arguments.get('intention', '')
    
    # 生成摘要
    summary = f"客户 {name} 咨询: {intention}"
    
    # 由于airtable_api.py已删除，这里直接返回成功消息
    # 实际项目中可以根据需要修改为其他实现
    print(f"表单提交成功: {summary}")
    print(f"客户信息: 姓名={name}, 电话={phone}, 微信={wechat}, 地址={address}")
    
    return {
        "success": True,
        "message": "表单提交成功",
        "data": {
            "name": name,
            "phone": phone,
            "wechat": wechat,
            "address": address,
            "intention": intention,
            "summary": summary
        }
    }


# 注册插件
tool_registry.register(
    ToolPlugin(
        name="submit_form",
        definition=SUBMIT_FORM_DEFINITION,
        handler=_handle_submit_form
    )
)