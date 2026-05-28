# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指引。

## 项目概述

企业知识库 RAG 系统 —— 一个 AI 驱动的问答应用，支持上传文档（PDF、DOCX、Markdown、TXT），进行文本切片与向量化，然后基于检索增强生成（RAG）回答用户问题。本项目定位为对标真实 AI 工程系统的学习/求职项目。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python、FastAPI、SQLAlchemy、PostgreSQL、Redis、Celery/RQ |
| AI/RAG | LangChain、LangGraph、Ollama、Qdrant、BGE Embedding、Rerank |
| 前端 | Next.js、React、TypeScript、TailwindCSS、shadcn/ui |
| 基础设施 | Docker Compose（postgres、redis、qdrant、ollama、backend、frontend） |

## 开发命令

### 环境变量
```bash
cp .env.example .env
```

### 启动基础设施（PostgreSQL、Redis、Qdrant）
```bash
docker compose up -d postgres redis qdrant
```

### 后端
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 健康检查
- 前端：http://localhost:3000
- 后端：http://localhost:8000/health
- API v1：http://localhost:8000/api/v1/health

## 架构设计

### 后端结构（`backend/app/`）

| 目录 | 职责 |
|------|------|
| `api/` | FastAPI 路由处理器（认证、知识库、文档、聊天） |
| `models/` | SQLAlchemy ORM 模型（users、knowledge_bases、documents、chunks、chats、messages） |
| `services/` | 业务逻辑层，衔接 API 与数据/AI 层 |
| `rag/` | RAG 流水线：查询改写 → 向量化 → 检索 → 重排序 → 上下文压缩 → 生成 |
| `agents/` | Agent 工具系统（文件查询、搜索、SQL、浏览器工具） |
| `embeddings/` | 文本向量化（BGE 模型） |
| `vectorstore/` | Qdrant 向量数据库集成 |
| `prompts/` | System/Template/Dynamic Prompt 管理 |
| `tasks/` | 异步任务定义（Celery/RQ），用于文档处理 |
| `utils/` | 通用工具函数 |

### 前端结构（`frontend/`）

| 目录 | 职责 |
|------|------|
| `app/` | Next.js App Router 页面 |
| `components/` | React 组件（聊天 UI、文档管理） |
| `hooks/` | 自定义 React Hooks |
| `lib/` | 通用工具与配置 |
| `services/` | API 客户端函数 |

### 核心 RAG 流程

```
用户提问 → 查询改写 → Embedding → Qdrant 检索 → Rerank 重排序 → 上下文压缩 → Prompt 构建 → LLM 推理 → 生成回答 + 引用来源
```

### 数据库设计（核心表）

- `users` —— 用户认证与角色（admin、user、guest）
- `knowledge_bases` —— 知识库，包含 Embedding 模型配置
- `documents` —— 上传的文档，带状态追踪（uploading → parsing → vectorizing → done/failed）
- `chunks` —— 文本片段，含元数据（filename、page、chunk_index、source、user_id）
- `chats` —— 对话会话，关联知识库
- `messages` —— 单条聊天消息（role、content）

### API 接口

- `POST /api/auth/register`、`POST /api/auth/login` —— JWT 认证
- `POST /api/kb/create`、`GET /api/kb/list`、`DELETE /api/kb/{id}` —— 知识库 CRUD
- `POST /api/document/upload`、`GET /api/document/list` —— 文档管理
- `POST /api/chat`、`GET /api/chat/history` —— RAG 问答

## 开发阶段

1. **第一阶段（当前）** —— 文档上传/解析/向量化、基础 RAG 问答、Chat UI
2. **第二阶段** —— 多轮对话、Rerank、Redis 缓存、Prompt 优化
3. **第三阶段** —— Agent 工具（SQL、浏览器、搜索）、LangGraph 工作流
4. **第四阶段** —— 多用户 RBAC、MCP 工具、Kubernetes 部署

## 关键设计决策

- 本地优先：Ollama 负责 LLM 推理，Qdrant 负责向量存储，全部通过 Docker 运行
- 推荐模型：Qwen 14B（问答）、DeepSeek R1（推理）、BGE（Embedding）
- 安全设计：JWT 认证、RBAC 权限控制、文件级权限、API 限流、Prompt Injection 防护
- 文档处理采用异步任务队列，避免阻塞 API 请求
