# 私人知识库系统

基于 Ollama DeepSeek 的智能问答知识库系统，支持文件夹监控、语义检索和自然语言问答。

## 🚀 特性

- **📄 文档处理**: 支持 PDF、Word、文本等多种文档格式
- **📁 文件夹监控**: 自动监控指定文件夹，实时构建知识库
- **🔍 智能检索**: 基于向量相似度的语义搜索
- **💬 智能问答**: 结合 DeepSeek 模型的自然语言问答
- **🗨️ 多轮对话**: 支持上下文记忆的对话功能
- **🌐 Web界面**: 简洁美观的用户界面
- **🔒 隐私安全**: 完全本地化部署，数据不外泄

## 📋 系统要求

- Python 3.8+
- Ollama (已安装 deepseek-r1:1.5b 模型)
- 8GB+ 内存推荐

## 🛠️ 安装部署

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 确保 Ollama 服务运行

```bash
# 启动 Ollama 服务
ollama serve

# 拉取 DeepSeek 模型
ollama pull deepseek-r1:1.5b
```

### 3. 配置系统

编辑 `config.py` 文件，根据需要调整配置：

```python
# Ollama配置
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:1.5b"

# 其他配置...
```

### 4. 启动系统

```bash
python main.py
```

系统将在 http://localhost:8000 启动。

## 📖 使用指南

### Web界面使用

1. **主页**: 查看系统状态和功能介绍
2. **文档管理**: 管理知识库文档，通过文件夹监控功能
3. **智能问答**: 与知识库进行问答交互

### 📁 文件夹监控功能

系统通过监控文件夹实现知识库的自动构建和管理。

#### 使用步骤：
1. 访问文档管理页面 (http://localhost:8000/docs-ui)
2. 在"文件夹监控"区域点击"启动监控"（系统启动时会自动开启监控）
3. 将文档文件放入监控文件夹：`./uploads/`
4. 系统会自动检测文件变化并更新知识库

#### 监控功能：
- ✅ **自动添加**: 检测新文件并自动添加到知识库
- 🔄 **自动更新**: 检测文件修改并更新知识库内容  
- 🗑️ **自动删除**: 检测文件删除并从知识库中移除
- 📊 **实时状态**: 显示监控状态和文件列表
- 🔍 **强制重扫**: 支持手动触发重新扫描

#### 支持格式：
- `.txt` - 纯文本文件

### API接口使用

#### 问答接口
```bash
curl -X POST "http://localhost:8000/api/question" \
     -H "Content-Type: application/json" \
     -d '{"question": "你的问题", "use_context": true}'
```

#### 查看文档列表
```bash
curl "http://localhost:8000/api/documents"
```

#### 文件夹监控接口
```bash
# 启动文件夹监控
curl -X POST "http://localhost:8000/api/folder-watch/start"

# 停止文件夹监控
curl -X POST "http://localhost:8000/api/folder-watch/stop"

# 查看监控状态
curl "http://localhost:8000/api/folder-watch/status"

# 强制重新扫描
curl -X POST "http://localhost:8000/api/folder-watch/rescan"
```

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web 界面      │    │   FastAPI       │    │   Ollama        │
│   (HTML/JS)     │◄──►│   (后端API)     │◄──►│   (DeepSeek)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   ChromaDB      │
                       │   (向量数据库)   │
                       └─────────────────┘
```

## 📁 项目结构

```
AIhw/
├── main.py                 # 主应用入口
├── config.py               # 配置文件
├── requirements.txt        # 依赖包
├── README.md              # 项目说明
├── models/                # 数据模型
│   ├── __init__.py
│   ├── document.py        # 文档处理模型
│   └── knowledge_base.py  # 知识库核心模型
├── services/              # 业务服务
│   ├── __init__.py
│   ├── ollama_service.py  # Ollama服务集成
│   └── folder_watcher.py  # 文件夹监控服务
├── api/                   # API接口
│   ├── __init__.py
│   └── routes.py          # 路由定义
└── templates/             # 网页模板
    ├── index.html         # 主页
    ├── docs.html          # 文档管理页
    └── chat.html          # 问答页面
```

## 🔧 高级配置

### 自定义嵌入模型

在 `config.py` 中修改：

```python
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

### 调整检索参数

```python
TOP_K_RESULTS = 10          # 检索结果数量
MAX_CONTEXT_LENGTH = 4000   # 最大上下文长度
```

### 文档处理设置

```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.md', '.csv']
```

## 🐛 问题排查

### 常见问题

1. **Ollama 连接失败**
   - 确保 Ollama 服务正在运行
   - 检查 `config.py` 中的 `OLLAMA_HOST` 配置

2. **问答无响应**
   - 检查知识库中是否有相关文档
   - 确认 DeepSeek 模型是否正确加载

3. **文件夹监控不工作**
   - 确认 `./uploads/` 文件夹存在
   - 检查文档格式是否在支持列表中
   - 查看控制台日志获取详细错误信息
   - 尝试手动重新扫描功能

### 日志查看

系统日志会输出到控制台，包含详细的错误信息。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请通过 Issue 或 Email 联系。

---

**注意**: 首次运行时会自动下载嵌入模型，可能需要一些时间。 