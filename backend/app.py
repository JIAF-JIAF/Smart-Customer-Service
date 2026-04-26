"""
智能客服 Agent 主应用
Flask Web 服务入口
"""

import uuid
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 导入模块
from modules.assistant import Assistant
from modules.vector_store import VectorStore
from modules.rag import RAG
from modules.ai_client import AIClient
from modules.prompt import PromptManager
from modules.context import Memory
 # 导入工具实例
from modules.tools.submit_form_plugin import submit_form_tool
from modules.tools.weather_plugin import weather_tool

# 确保系统默认编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
    import codecs
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 确保 JSON 响应不使用 ASCII 编码
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'  # 统一设置 MIME 类型
CORS(app)  # 允许前端跨域访问

# 全局变量
assistant_instance = None
vector_store_instance = None
rag_instance = None
sessions = {}  # 存储会话线程映射


def init_system():
    """初始化系统组件"""
    global assistant_instance, vector_store_instance, rag_instance

    print("=" * 50)
    print("智能客服系统启动中...")
    print("=" * 50)

    # 1. 初始化 AI 客户端
    print("\n[1/4] 初始化 AI 客户端...")
    try:
        ai_client = AIClient(config_path="config.json")
        print("AI 客户端初始化完成")
    except Exception as e:
        print("AI 客户端初始化失败: {}".format(e))
        raise

    # 2. 初始化知识库
    print("\n[2/4] 初始化知识库...")
    try:
        vector_store_instance = VectorStore(ai_client=ai_client)
        kb_data = vector_store_instance.init_knowledge_base()
        print("知识库初始化完成")
    except Exception as e:
        print("知识库初始化警告: {}".format(e))
        kb_data = None

    # 3. 初始化 RAG
    print("\n[3/4] 初始化 RAG 检索器...")
    try:
        rag_instance = RAG(kb_data)
        print("RAG 检索器初始化完成")
    except Exception as e:
        print("RAG 初始化警告: {}".format(e))
        rag_instance = RAG(kb_data)

    # 4. 初始化助手
    print("\n[4/4] 初始化 AI 助手...")
    try:
        # 初始化 Prompt 管理器
        prompt_manager = PromptManager()
        # 初始化记忆管理器
        memory_instance = Memory()
        
        assistant_instance = Assistant(options={
            "prompt": prompt_manager.get_prompt("customer_service"),
            "ragModule": rag_instance,
            "vectorStore": vector_store_instance,
            "tools": [submit_form_tool, weather_tool],
            "aiClient": ai_client,
            "memory": memory_instance
        })
        assistant_instance.init_client()
        print("AI 助手初始化完成")
    except Exception as e:
        print("AI 助手初始化失败: {}".format(e))
        raise

    # 5. 打印状态
    print("\n[5/5] 系统状态检查...")
    print("  - API 客户端: {}  ".format("成功" if assistant_instance.client else "失败"))
    print("  - 模型: {}".format(assistant_instance.model))
    print("  - 知识库: {}  ".format("成功" if vector_store_instance else "失败"))
    print("  - RAG: {}  ".format("成功" if rag_instance else "失败"))

    print("\n" + "=" * 50)
    print("智能客服系统就绪!")
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

        print("\n[对话请求] Session: {}".format(session_id))
        print("用户: {}".format(user_message))

        # 2. 处理完整的对话流程
        result = assistant_instance.process_message(session_id, user_message)
        
        # 3. 返回结果
        return jsonify(result)
        
    except Exception as e:
        print("对话处理异常: {}".format(e))
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