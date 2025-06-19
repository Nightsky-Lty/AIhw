# API 接口文档

私人知识库系统 API 接口说明

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **Content-Type**: `application/json`
- **编码**: UTF-8

## 文档管理接口

### 获取文档列表

**接口地址**: `GET /documents`

**描述**: 获取知识库中所有文档的列表

**响应示例**:
```json
{
  "success": true,
  "documents": [
    {
      "id": "doc-uuid-1",
      "filename": "example.pdf",
      "chunk_count": 15
    }
  ]
}
```

### 删除文档

**接口地址**: `DELETE /documents/{document_id}`

**描述**: 从知识库中删除指定文档

**路径参数**:
- `document_id`: 文档ID

**响应示例**:
```json
{
  "success": true,
  "message": "文档删除成功"
}
```

### 搜索文档

**接口地址**: `GET /search`

**描述**: 在知识库中搜索相关内容

**查询参数**:
- `q`: 搜索关键词 (必填)
- `limit`: 返回结果数量 (可选，默认5)

**响应示例**:
```json
{
  "success": true,
  "query": "Python编程",
  "results": [
    {
      "content": "Python是一种高级编程语言...",
      "metadata": {
        "document_id": "doc-uuid-1",
        "filename": "python_guide.pdf",
        "chunk_index": 3
      },
      "similarity": 0.95
    }
  ]
}
```

## 问答接口

### 单次问答

**接口地址**: `POST /question`

**描述**: 基于知识库内容回答单个问题

**请求体**:
```json
{
  "question": "什么是机器学习？",
  "use_context": true
}
```

**响应示例**:
```json
{
  "success": true,
  "question": "什么是机器学习？",
  "answer": "机器学习是人工智能的一个分支...",
  "context_used": true,
  "sources": 3
}
```

### 多轮对话

**接口地址**: `POST /chat`

**描述**: 支持上下文记忆的多轮对话

**请求体**:
```json
{
  "messages": [
    {"role": "user", "content": "什么是Python？"},
    {"role": "assistant", "content": "Python是一种编程语言..."},
    {"role": "user", "content": "它有什么特点？"}
  ],
  "use_context": true
}
```

**响应示例**:
```json
{
  "success": true,
  "answer": "Python的主要特点包括...",
  "context_used": true,
  "sources": 2
}
```

## 文件夹监控接口

### 启动文件夹监控

**接口地址**: `POST /folder-watch/start`

**描述**: 启动文件夹监控服务，自动检测uploads文件夹中的文件变化

**响应示例**:
```json
{
  "success": true,
  "message": "文件夹监控已启动",
  "watch_folder": "/path/to/uploads"
}
```

### 停止文件夹监控

**接口地址**: `POST /folder-watch/stop`

**描述**: 停止文件夹监控服务

**响应示例**:
```json
{
  "success": true,
  "message": "文件夹监控已停止"
}
```

### 获取监控状态

**接口地址**: `GET /folder-watch/status`

**描述**: 获取文件夹监控服务的当前状态

**响应示例**:
```json
{
  "success": true,
  "status": {
    "is_running": true,
    "watch_folder": "/path/to/uploads",
    "tracked_files": 5,
    "supported_extensions": [".txt"],
    "files": [
      {
        "path": "/path/to/uploads/doc1.txt",
        "name": "doc1.txt",
        "document_id": "doc-uuid-1"
      }
    ]
  }
}
```

### 强制重新扫描

**接口地址**: `POST /folder-watch/rescan`

**描述**: 强制重新扫描监控文件夹，重新构建知识库

**响应示例**:
```json
{
  "success": true,
  "message": "强制重新扫描完成"
}
```

## 系统信息接口

### 获取统计信息

**接口地址**: `GET /stats`

**描述**: 获取知识库统计信息

**响应示例**:
```json
{
  "success": true,
  "stats": {
    "total_chunks": 150,
    "total_documents": 10,
    "documents": [
      {
        "id": "doc-uuid-1",
        "filename": "example.pdf",
        "chunk_count": 15
      }
    ]
  }
}
```

### 健康检查

**接口地址**: `GET /health`

**描述**: 检查系统健康状态

**响应示例**:
```json
{
  "success": true,
  "status": "healthy",
  "ollama_available": true,
  "model": "deepseek-r1:1.5b"
}
```

## 使用说明

### 文档添加方式

系统不再支持通过API上传文件，而是采用文件夹监控方式自动添加文档：

1. 将文件放入 `uploads` 文件夹
2. 系统自动检测并添加到知识库
3. 支持的文件格式：.txt

### 文件夹监控工作流程

1. 启动监控：`POST /folder-watch/start`
2. 添加文件到 `uploads` 文件夹
3. 系统自动处理文件变化（新增、修改、删除）
4. 查看状态：`GET /folder-watch/status`
5. 需要时可以强制重新扫描：`POST /folder-watch/rescan`
6. 停止监控：`POST /folder-watch/stop`

## 错误响应

所有接口在出错时都会返回统一的错误格式：

```json
{
  "success": false,
  "detail": "错误详细信息"
}
```

常见错误状态码：
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 使用示例

### Python 示例

```python
import requests

# 启动文件夹监控
response = requests.post('http://localhost:8000/api/folder-watch/start')
print(response.json())

# 问答
response = requests.post(
    'http://localhost:8000/api/question',
    json={
        'question': '什么是机器学习？',
        'use_context': True
    }
)
print(response.json())
```

### JavaScript 示例

```javascript
// 启动文件夹监控
async function startMonitoring() {
    const response = await fetch('/api/folder-watch/start', {
        method: 'POST'
    });
    const data = await response.json();
    console.log(data);
}

// 问答
async function askQuestion(question) {
    const response = await fetch('/api/question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            question: question,
            use_context: true
        })
    });
    const data = await response.json();
    return data.answer;
}
```

## 注意事项

1. **文件大小限制**: 单个文件最大支持 10MB
2. **支持格式**: 仅支持 .txt 格式
3. **监控文件夹**: 默认监控 `./uploads/` 文件夹
4. **并发限制**: 建议避免同时上传过多文档
5. **Ollama 依赖**: 问答功能需要 Ollama 服务正常运行 