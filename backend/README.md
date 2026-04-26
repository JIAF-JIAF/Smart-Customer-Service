# 智能客服系统后端

基于 Flask 和 OpenAI API 构建的智能客服系统后端，支持知识库检索、工具调用和多轮对话。

## 项目结构

```
backend/
├── app.py                  # 主应用入口
├── config.json             # 配置文件
├── assistant.json          # 助手配置（系统提示词）
├── modules/                # 核心模块
│   ├── __init__.py         # 模块导出
│   ├── ai_client.py        # AI 客户端管理
│   ├── assistant.py        # 智能助手
│   ├── vector_store.py     # 向量存储
│   ├── rag.py              # RAG 检索器
│   └── prompt/             # Prompt 管理
│       └── __init__.py
├── modules/tools/          # 工具插件
│   ├── submit_form_plugin.py  # 提交表单工具
│   └── weather_plugin.py      # 天气查询工具
├── knowledge_base/         # 知识库目录
├── db/                     # 向量存储目录
├── requirements.txt        # 依赖包
└── README.md               # 项目说明
```

## 核心功能

1. **智能客服对话**：基于 OpenAI API 实现的智能对话能力
2. **知识库检索**：支持从文档中检索相关信息
3. **工具调用**：支持调用外部工具（如提交表单、查询天气）
4. **会话管理**：支持多轮对话和上下文保持

## 技术架构

### 模块说明

| 模块 | 职责 | 类名 |
|------|------|------|
| AI 客户端 | 管理 OpenAI API 客户端 | `AIClient` |
| 向量存储 | 文档向量化和知识库管理 | `VectorStore` |
| RAG 检索器 | 从知识库中检索相关内容 | `RAG` |
| Prompt 管理 | 管理系统提示词 | `PromptManager` |
| 智能助手 | 处理用户对话和工具调用 | `Assistant` |

### 数据流

1. 用户发送请求到 `/chat` 接口
2. 系统初始化各个模块（AI 客户端、向量存储、RAG、Prompt 管理器）
3. 智能助手处理用户输入，进行 RAG 检索增强
4. 调用 OpenAI API 生成回复
5. 如果需要工具调用，执行相应工具并获取结果
6. 返回最终回复给用户

## 快速开始

### 环境要求

- Python 3.8+
- Flask 2.0+
- OpenAI API 密钥

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

编辑 `config.json` 文件，设置 API 密钥和基础 URL：

```json
{
  "api_key": "your_api_key",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "deepseek-v4-pro",
  "embedding_model": "text-embedding-v3"
}
```

### 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## API 接口

### 1. 检查服务状态

- **路径**: `/start`
- **方法**: `GET`
- **返回**: 服务状态信息

### 2. 发送对话请求

- **路径**: `/chat`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "message": "你好，我想了解产品信息",
    "session_id": "user123"
  }
  ```
- **返回**:
  ```json
  {
    "reply": "您好！很高兴为您服务。请问您想了解哪款产品的信息呢？",
    "session_id": "user123",
    "status": "success"
  }
  ```

## 知识库管理

1. 在 `knowledge_base` 目录中添加文档（支持 .txt、.pdf、.docx 格式）
2. 重启服务时会自动索引文档到向量存储
3. 系统会在回复用户时自动检索相关知识

## 工具扩展

可以在 `modules/tools` 目录中添加自定义工具，遵循以下格式：

```python
class YourTool:
    def __init__(self):
        self.name = "your_tool"
        self.description = "工具描述"
    
    def run(self, params):
        # 工具逻辑
        return {"result": "工具执行结果"}
    
    def get_definition(self):
        # 返回工具定义
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        # 参数定义
                    },
                    "required": []
                }
            }
        }

# 导出工具实例
your_tool = YourTool()
```

然后在 `app.py` 中导入并添加到工具列表。

## 架构优势

1. **模块化设计**：各模块职责清晰，易于扩展
2. **资源共享**：所有模块使用同一个 AI 客户端实例
3. **配置集中**：API 配置统一管理在 config.json
4. **面向对象**：使用类实例化方式，结构清晰
5. **向后兼容**：保持了原有接口的兼容性

## 注意事项

1. 确保设置了正确的 OpenAI API 密钥和基础 URL
2. 知识库文档需要放在 `knowledge_base` 目录中
3. 首次启动会自动索引知识库，可能需要一些时间
4. 工具调用需要遵循 OpenAI 的函数调用格式

## 故障排查

- **API 调用失败**：检查 API 密钥和网络连接
- **知识库检索失败**：检查知识库目录和文档格式
- **工具调用失败**：检查工具参数和实现逻辑
- **服务启动失败**：检查端口是否被占用，依赖是否安装完整

## 许可证

MIT
