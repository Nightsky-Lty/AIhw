# API 文档

## 基础信息

- 基础URL: `http://localhost:8000`
- 所有请求和响应均使用 JSON 格式

## 接口列表

### 1. 文本问答

#### 请求

- 方法: `POST`
- 路径: `/api/chat`
- Content-Type: `application/json`

请求体格式：
```json
{
    "prompt": "你好，请问你是谁？",
    "max_length": 2048,  // 可选，默认2048
    "temperature": 0.7   // 可选，默认0.7
}
```

#### 响应

```json
{
    "response": "你好！我是基于DEEPSEEK-Coder的AI助手，专门擅长代码相关的问题和编程任务。",
    "status": "success"
}
```

### 2. 健康检查

#### 请求

- 方法: `GET`
- 路径: `/health`

#### 响应

```json
{
    "status": "ok",
    "model_loaded": true
}
```

## 错误处理

所有错误响应都将包含以下格式：

```json
{
    "error": "错误描述信息",
    "status": "error"
}
```

常见错误码：
- 400: 请求参数错误
- 500: 服务器内部错误
- 503: 模型未加载完成 