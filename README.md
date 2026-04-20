# 🤖 扫地机器人智能客服 Agent

> 基于 LangGraph + RAG 的多工具智能客服系统，面向扫地机器人领域，支持知识库问答、实时天气查询、用户报告生成等功能。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能特性

- **RAG 知识库问答**：支持 PDF/TXT 文档向量化检索，通过 MD5 去重实现增量更新。
- **ReAct Agent 工具调用**：Agent 自主决策调用知识库检索、实时天气、用户位置、外部数据查询等工具。
- **动态提示词切换**：通过 LangGraph 中间件检测用户意图，自动在普通问答与报告生成模式间切换系统提示词。
- **对话历史持久化**：基于 SQLite 存储对话记录，侧边栏支持历史会话加载与删除。
- **双端服务**：
  - Streamlit Web 界面，支持流式打字机效果。
  - FastAPI RESTful API，提供标准 HTTP 接口与 Swagger 文档。
- **容器化支持**：提供 `Dockerfile` 与 `docker-compose.yml`，可一键部署。

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| Agent 框架 | LangChain + LangGraph |
| 大语言模型 | 通义千问 (DashScope) |
| 嵌入模型 | DashScope Embedding |
| 向量数据库 | Chroma |
| Web 框架 | Streamlit + FastAPI |
| 数据持久化 | SQLite |
| 配置管理 | YAML + python-dotenv |
| 日志系统 | Python logging |
| 容器化 | Docker + Docker Compose |

## 📁 项目结构
````
.
├── agent/ # Agent 核心逻辑与工具
│ ├── tools/ # 工具函数与中间件
│ │ ├── agent_tools.py # 所有工具定义（RAG、天气、用户信息等）
│ │ └── middleware.py # 中间件（日志、动态提示词切换）
│ └── react_agent.py # ReAct Agent 封装
├── rag/ # RAG 知识库服务
│ ├── vector_store.py # 向量库构建与检索
│ └── rag_service.py # RAG 总结服务
├── model/ # 模型工厂
│ └── factory.py # ChatModel 与 Embedding 工厂
├── utils/ # 工具模块
│ ├── config_handler.py # YAML 配置加载
│ ├── db_handler.py # SQLite 对话历史管理
│ ├── file_handler.py # 文件 MD5、PDF/TXT 加载
│ ├── logger_handler.py # 统一日志
│ ├── path_tool.py # 项目路径管理
│ └── prompt_loader.py # 提示词加载
├── config/ # YAML 配置文件
├── data/ # 知识库文档与外部数据
├── prompts/ # 提示词模板
├── logs/ # 日志输出目录
├── app.py # Streamlit 入口
├── api_server.py # FastAPI 入口
├── requirements.txt # Python 依赖
├── Dockerfile # Docker 构建文件
└── docker-compose.yml # Docker Compose 编排
````

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Ccccc-zm/react-agent-knowledge-base.git
cd react-agent-knowledge-base
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```
### 3. 配置环境变量
在项目根目录创建 .env 文件，填入以下内容（请替换为你的真实密钥）：
```
# 通义千问 API（必填）
DASHSCOPE_API_KEY=你的通义千问API密钥

# 和风天气 API（可选，用于天气查询）
QWEATHER_API_HOST=你的和风天气Host
QWEATHER_API_KEY=你的和风天气API Key
```
注意：.env 文件已被 .gitignore 忽略，不会被提交到 GitHub。

### 4. 构建知识库（首次运行）
将你的 PDF 或 TXT 文档放入 data/ 目录，然后执行：
```
python rag/vector_store.py
```
脚本会自动扫描文件、计算 MD5、分割文本、向量化并存入 Chroma。已处理过的文件不会重复处理。

### 5. 启动服务
方式一：Streamlit 界面（推荐）
```
streamlit run app.py
```
访问 http://localhost:8501，即可在聊天界面与智能客服对话。

方式二：FastAPI 接口
```
python api_server.py
```
访问 http://localhost:8000/docs 查看 Swagger 交互式 API 文档。

### 6. 使用 Docker

确保 Docker Desktop 已安装并运行，然后执行：
```
docker-compose up -d --build
```
服务启动后：
- Streamlit：`http://localhost:8501`
- FastAPI：`http://localhost:8000/docs`

## 💬 对话示例

| 用户提问 | Agent 行为 |
|----------|------------|
| "小户型适合哪些扫地机器人？" | 调用 RAG 工具，从知识库检索相关信息并总结回答 |
| "北京今天天气怎么样？" | 调用和风天气 API，返回实时天气数据 |
| "给我生成我的使用报告" | 调用外部数据工具，切换报告提示词，生成结构化报告 |

## 📌 注意事项

- 首次运行前务必执行 `python rag/vector_store.py` 构建向量库。
- 确保 `.env` 中的 API Key 有效，且阿里云账户余额充足。
- 知识库文档支持 `.pdf` 和 `.txt` 格式，放置在 `data/` 目录下。
- Chroma 向量数据默认保存在 `chroma_db/` 目录，可删除后重新构建。

## 🙏 致谢

本项目参考了 LangChain 官方文档、LangGraph 中间件机制以及社区优秀实践，在此表示感谢。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。