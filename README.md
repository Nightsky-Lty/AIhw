# AI大作业 - 大语言模型部署

本项目实现了一个基于DEEPSEEK模型的本地部署方案，支持基本的短文本问答功能。

## 模型说明

当前使用DEEPSEEK-Coder 1.3B模型，这是一个专门为代码生成和理解优化的轻量级模型：
- 参数量：1.3B，适合CPU推理
- 内存需求：约4-6GB
- 支持多种编程语言的代码理解和生成

## 环境要求

- Python 3.8+
- CPU（如有GPU更佳）
- 至少8GB内存（推荐16GB以上）

## 安装步骤

1. 克隆项目并进入项目目录
```bash
git clone [your-repo-url]
cd [project-directory]
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

1. 启动服务器
```bash
python main.py
```

2. 访问API文档
打开浏览器访问：http://localhost:8000/docs

## API接口

详细接口文档请参考 `docs/api.md`

## 项目结构

```
.
├── README.md
├── requirements.txt
├── main.py                 # 主程序入口
├── app/
│   ├── __init__.py
│   ├── config.py          # 配置文件
│   ├── model.py           # 模型加载和推理
│   └── api.py             # API路由
└── docs/
    └── api.md             # API文档
``` 