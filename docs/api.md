# API 接口文档

私人知识库系统 API 接口详细说明。

## 基础信息

- **基础URL**: `http://localhost:8000/api`
- **认证方式**: 无需认证
- **请求格式**: JSON
- **响应格式**: JSON

## 接口列表

### 1. 文档管理

#### 1.1 上传文档

**接口**: `POST /upload`

**描述**: 上传文档到知识库

**请求参数**:
- `file` (File): 要上传的文件

**支持格式**: `.txt`, `.pdf`, `.docx`, `.md`

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/upload" \
     -F "file=@example.pdf"
```

**响应示例**:
```json
{
    "success": true,
    "message": "文档上传成功",
    "document_id": "uuid-string",
    "filename": "example.pdf"
}
```

#### 1.2 获取文档列表

**接口**: `GET /documents`

**描述**: 获取知识库中所有文档的列表

**请求示例**:
```bash
curl "http://localhost:8000/api/documents"
```

**响应示例**:
```json
{
    "success": true,
    "documents": [
        {
            "id": "uuid-string",
            "filename": "example.pdf",
            "chunk_count": 10
        }
    ]
}
```

#### 1.3 删除文档

**接口**: `DELETE /documents/{document_id}`

**描述**: 从知识库中删除指定文档

**路径参数**:
- `document_id` (string): 文档ID

**请求示例**:
```bash
curl -X DELETE "http://localhost:8000/api/documents/uuid-string"
```

**响应示例**:
```json
{
    "success": true,
    "message": "文档删除成功"
}
```

### 2. 知识检索

#### 2.1 搜索文档

**接口**: `GET /search`

**描述**: 在知识库中搜索相关内容

**查询参数**:
- `q` (string): 搜索查询
- `limit` (int, 可选): 返回结果数量，默认为5

**请求示例**:
```bash
curl "http://localhost:8000/api/search?q=人工智能&limit=3"
```

**响应示例**:
```json
{
    "success": true,
    "query": "人工智能",
    "results": [
        {
            "content": "文档内容片段...",
            "metadata": {
                "document_id": "uuid-string",
                "filename": "ai_guide.pdf",
                "chunk_index": 0
            },
            "similarity": 0.85
        }
    ]
}
```

### 3. 智能问答

#### 3.1 单次问答

**接口**: `POST /question`

**描述**: 基于知识库内容回答问题

**请求参数**:
```json
{
    "question": "string",      // 用户问题
    "use_context": true        // 是否使用知识库上下文
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/question" \
     -H "Content-Type: application/json" \
     -d '{
         "question": "什么是人工智能？",
         "use_context": true
     }'
```

**响应示例**:
```json
{
    "success": true,
    "question": "什么是人工智能？",
    "answer": "人工智能是...",
    "context_used": true,
    "sources": 3
}
```

#### 3.2 多轮对话

**接口**: `POST /chat`

**描述**: 支持多轮对话的问答接口

**请求参数**:
```json
{
    "messages": [
        {
            "role": "user",
            "content": "第一个问题"
        },
        {
            "role": "assistant", 
            "content": "第一个回答"
        },
        {
            "role": "user",
            "content": "第二个问题"
        }
    ],
    "use_context": true
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
         "messages": [
             {"role": "user", "content": "介绍一下机器学习"},
             {"role": "assistant", "content": "机器学习是..."},
             {"role": "user", "content": "它有哪些应用？"}
         ],
         "use_context": true
     }'
```

**响应示例**:
```json
{
    "success": true,
    "answer": "机器学习的应用包括...",
    "context_used": true,
    "sources": 2
}
```

### 4. 系统信息

#### 4.1 获取统计信息

**接口**: `GET /stats`

**描述**: 获取知识库统计信息

**请求示例**:
```bash
curl "http://localhost:8000/api/stats"
```

**响应示例**:
```json
{
    "success": true,
    "stats": {
        "total_chunks": 150,
        "total_documents": 10,
        "documents": [
            {
                "id": "uuid-string",
                "filename": "example.pdf",
                "chunk_count": 15
            }
        ]
    }
}
```

#### 4.2 健康检查

**接口**: `GET /health`

**描述**: 检查系统健康状态

**请求示例**:
```bash
curl "http://localhost:8000/api/health"
```

**响应示例**:
```json
{
    "success": true,
    "status": "healthy",
    "ollama_available": true,
    "model": "deepseek-r1:1.5b"
}
```

## 错误处理

### 错误响应格式

```json
{
    "success": false,
    "detail": "错误描述信息"
}
```

### 常见错误代码

- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `413 Payload Too Large`: 文件过大
- `500 Internal Server Error`: 服务器内部错误

### 具体错误示例

#### 文件类型不支持
```json
{
    "success": false,
    "detail": "不支持的文件类型。支持的类型: .txt, .pdf, .docx, .md"
}
```

#### 文件过大
```json
{
    "success": false,
    "detail": "文件过大。最大支持 10MB"
}
```

#### Ollama服务不可用
```json
{
    "success": false,
    "detail": "连接Ollama服务失败: Connection refused"
}
```

## 使用建议

### 1. 最佳实践

- **文档上传**: 建议将大文档分割成较小的部分上传
- **问答查询**: 问题越具体，答案越准确
- **批量操作**: 避免并发大量请求，建议控制频率

### 2. 性能优化

- **缓存策略**: 系统会自动缓存嵌入向量
- **模型预热**: 首次使用可能较慢，后续会更快
- **资源管理**: 大量文档时注意内存使用

### 3. 安全注意事项

- **文件验证**: 系统会验证文件类型和大小
- **内容过滤**: 建议在生产环境中添加内容审核
- **访问控制**: 根据需要添加身份验证机制

## 示例代码

### Python 客户端示例

```python
import requests
import json

class KnowledgeBaseClient:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
    
    def upload_document(self, file_path):
        """上传文档"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/upload", files=files)
            return response.json()
    
    def ask_question(self, question, use_context=True):
        """提问"""
        data = {
            "question": question,
            "use_context": use_context
        }
        response = requests.post(f"{self.base_url}/question", json=data)
        return response.json()
    
    def get_documents(self):
        """获取文档列表"""
        response = requests.get(f"{self.base_url}/documents")
        return response.json()

# 使用示例
client = KnowledgeBaseClient()

# 上传文档
result = client.upload_document("document.pdf")
print(f"上传结果: {result}")

# 提问
answer = client.ask_question("文档的主要内容是什么？")
print(f"回答: {answer['answer']}")
```

### JavaScript 客户端示例

```javascript
class KnowledgeBaseClient {
    constructor(baseUrl = 'http://localhost:8000/api') {
        this.baseUrl = baseUrl;
    }
    
    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseUrl}/upload`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    async askQuestion(question, useContext = true) {
        const response = await fetch(`${this.baseUrl}/question`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                use_context: useContext
            })
        });
        
        return await response.json();
    }
    
    async getDocuments() {
        const response = await fetch(`${this.baseUrl}/documents`);
        return await response.json();
    }
}

// 使用示例
const client = new KnowledgeBaseClient();

// 上传文档
document.getElementById('fileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const result = await client.uploadDocument(file);
        console.log('上传结果:', result);
    }
});

// 提问
async function askQuestion() {
    const question = document.getElementById('questionInput').value;
    const answer = await client.askQuestion(question);
    console.log('回答:', answer.answer);
}
```

---

更多详细信息请参考项目 README.md 文件。 