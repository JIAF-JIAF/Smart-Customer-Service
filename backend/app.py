"""
智能客服 Agent 主应用
Flask Web 服务入口
"""

import json
import time
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入模块
from modules.assistant import get_assistant, Assistant
from modules.vector_store import get_vector_store
from modules.tools import execute_tool

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

# 全局变量
assistant_instance = None
vector_store_instance = None
sessions = {}  # 存储会话线程映射


def init_system():
    """初始化系统组件"""
    global assistant_instance, vector_store_instance
    
    print("=" * 50)
    print("智能客服系统启动中...")
    print("=" * 50)
    
    # 1. 初始化知识库
    print("\n[1/3] 初始化知识库...")
    try:
        vector_store_instance = get_vector_store()
        vector_store_instance.init_knowledge_base()
        print("✓ 知识库初始化完成")
    except Exception as e:
        print(f"⚠ 知识库初始化警告: {e}")
    
    # 2. 初始化助手
    print("\n[2/3] 初始化AI助手...")
    try:
        assistant_instance = get_assistant()
        print("✓ AI助手初始化完成")
    except Exception as e:
        print(f"✗ AI助手初始化失败: {e}")
        raise
    
    # 3. 打印状态
    print("\n[3/3] 系统状态检查...")
    print(f"  - API 客户端: {'✓' if assistant_instance.client else '✗'}")
    print(f"  - 模型: {assistant_instance.model}")
    print(f"  - 知识库: {'✓' if vector_store_instance else '✗'}")
    
    print("\n" + "=" * 50)
    print("✓ 智能客服系统就绪!")
    print("=" * 50)
    print("\n服务地址: http://localhost:5000")
    print("API 文档:")
    print("  GET  /start  - 检查服务状态")
    print("  POST /chat   - 发送对话请求")
    print("=" * 50 + "\n")


@app.route('/start', methods=['GET'])
def start():
    """
    GET /start
    检查服务状态
    """
    try:
        status = {
            "status": "ready",
            "message": "客服系统已就绪",
            "model": assistant_instance.model if assistant_instance else None,
            "knowledge_base": vector_store_instance.check_knowledge_base_exists() if vector_store_instance else False
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/chat', methods=['POST'])
def chat():
    """
    POST /chat
    处理对话请求
    
    请求体:
    {
        "message": "用户输入的内容",
        "session_id": "可选的会话标识"
    }
    
    响应:
    {
        "reply": "AI 回复内容",
        "tool_calls": [],
        "session_id": "会话ID",
        "finished": false
    }
    """
    try:
        # 1. 接收请求数据
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "error": "缺少 message 字段"
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        print(f"\n[对话请求] Session: {session_id}")
        print(f"用户: {user_message}")
        
        # 2. 调用助手对话
        result = assistant_instance.chat(session_id, user_message)
        
        # 3. 检查是否需要调用工具
        if result['tool_calls']:
            print(f"检测到 {len(result['tool_calls'])} 个工具调用")
            
            for tool_call in result['tool_calls']:
                tool_name = tool_call['name']
                tool_args = tool_call['arguments']
                tool_call_id = tool_call['id']
                
                print(f"调用工具: {tool_name}")
                print(f"参数: {tool_args}")
                
                # 执行工具
                tool_result = execute_tool(tool_name, tool_args)
                print(f"工具执行结果: {tool_result}")
                
                # 提交工具结果并获取最终回复
                final_reply = assistant_instance.submit_tool_result(
                    session_id, 
                    tool_call_id, 
                    tool_result
                )
                
                print(f"AI: {final_reply}")
                
                return jsonify({
                    "reply": final_reply,
                    "tool_calls": [tool_call],
                    "session_id": session_id,
                    "finished": False
                })
        
        # 4. 无工具调用,直接返回
        print(f"AI: {result['content']}")
        
        return jsonify({
            "reply": result['content'],
            "tool_calls": [],
            "session_id": session_id,
            "finished": False
        })
        
    except Exception as e:
        print(f"对话处理异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == '__main__':
    # 初始化系统
    init_system()
    
    # 启动 Flask 服务
    app.run(host='0.0.0.0', port=5000, debug=True)
