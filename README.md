# 智能客服系统 🤖

一个基于 AI 的智能客服系统，采用前后端分离架构，支持知识库检索、工具调用和多轮对话。

## ✨ 特色功能

- **智能知识库**: 自动向量化文本，基于相似度检索相关知识
- **RAG 增强**: 检索增强生成，提升 AI 回答的准确性和相关性
- **上下文管理 & 多轮对话**: 独立上下文管理器维护会话历史，支持连续对话
- **工具调用**: AI 可自主判断并调用外部工具（如天气查询、表单提交）
- **前后端分离**: React 前端 + Flask 后端，易于扩展和维护
- **模块化设计**: 清晰的架构，方便功能扩展
- **配置化管理**: JSON 配置文件，灵活可调

## 📁 项目结构

```
customer/
├── backend/              # Python 后端 (Flask)
│   ├── app.py           # Flask 主应用
│   ├── config.json      # 系统配置
│   ├── requirements.txt # Python 依赖
│   ├── .env             # 环境变量
│   ├── modules/         # 后端模块
│   │   ├── assistant.py    # AI 助手管理
│   │   ├── vector_store.py # 知识库向量化
│   │   ├── context/        # 上下文管理
│   │   │   ├── __init__.py
│   │   │   └── context_manager.py
│   │   ├── rag.py          # RAG 检索模块
│   │   └── tools/          # 工具插件
│   │       ├── __init__.py
│   │       ├── weather_plugin.py
│   │       └── submit_form_plugin.py
│   └── ...
│
└── frontend/            # React 前端 (Vite)
    ├── src/
    │   ├── components/  # UI 组件
    │   ├── api/         # API 调用
    │   └── ...
    └── package.json
```

## 🚀 快速开始

### 环境要求

- Python >= 3.8
- Node.js >= 16
- npm 或 yarn

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 编辑 .env 文件，填入你的 API Key

# 启动服务
python app.py
```

后端将运行在: `http://localhost:5000`

### 前端启动

打开新终端：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在: `http://localhost:5173`

### 访问应用

在浏览器中打开: `http://localhost:5173`

## 🔧 配置说明

### 系统配置 (config.json)

```json
{
  "api_key": "API_Key",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-plus",
  "embedding_model": "text-embedding-v3",
  "assistant_id": null,
  "knowledge_base_path": "knowledge_base.json",
  "assistant_config_path": "assistant.json"
}
```

## 📡 API 接口

### GET /start
检查服务状态

**响应示例:**
```json
{
  "status": "ready",
  "message": "客服系统已就绪",
  "assistant_id": "asst_xxx",
  "knowledge_base": true
}
```

### POST /chat
处理对话请求

**请求体:**
```json
{
  "message": "用户输入",
  "session_id": "可选会话ID"
}
```

**响应示例:**
```json
{
  "reply": "AI回复内容",
  "tool_calls": [],
  "session_id": "会话ID",
  "finished": false
}
```

## 🎯 使用流程

1. **准备知识库**: 编辑 `backend/data/raw_knowledge.txt`，添加你的业务知识
2. **启动服务**: 按照上面的步骤启动前后端服务
3. **开始对话**: 在浏览器中访问前端地址，与智能客服对话
4. **RAG 增强**: 系统会自动从知识库中检索相关信息，增强 AI 的回答
5. **工具调用**: 当客户需要提供信息时，AI 会自动调用表单提交工具；当客户询问天气时，AI 会自动调用天气查询工具

## 🛠️ 自定义扩展

### 修改助手指令
编辑 `backend/assistant.json` 中的 `instructions` 字段来调整 AI 的行为

### 添加新工具
1. 在 `backend/modules/tools/` 目录下创建新的插件文件
2. 定义工具实例，包含名称、定义和处理函数
3. 在插件文件末尾创建并导出工具实例
4. 在 `app.py` 中导入新的工具实例并添加到工具列表
5. 重启服务，新工具会被注册并使用

### 更新知识库
1. 修改 `backend/data/raw_knowledge.txt`
2. 删除 `backend/knowledge_base.json`
3. 重启服务，系统会自动重新向量化

## 📊 技术栈

**后端**:
- Flask 3.0.0 - Web 框架
- OpenAI SDK 1.12.0 - AI API 客户端 (兼容阿里云百炼)
- Flask-CORS - 跨域支持
- numpy 2.4.4 - 数值计算 (用于向量相似度计算)
- RAG 技术 - 检索增强生成

**前端**:
- React 18 - UI 框架
- Vite - 构建工具
- Axios - HTTP 请求
- UUID - 会话管理

**AI 服务**:
- 阿里云百炼平台
- qwen-plus 模型
- text-embedding-v3 向量化模型


## 🔮 后续优化建议

- [x] 添加缓存机制提升性能
- [ ] 支持更多向量数据库
- [ ] 实现数据库替代 JSON 存储
- [ ] 添加 API 限流和安全验证
- [ ] Docker 容器化部署
- [-] 多轮对话策略优化