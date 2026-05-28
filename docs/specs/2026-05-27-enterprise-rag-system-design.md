# 企业知识库 RAG 系统 — 设计文档

> 日期：2026-05-27
> 状态：已确认
> 类型：AI 工程实战学习项目

---

## 一、项目定位

按真实 AI 工程系统标准构建的企业知识库 RAG 问答应用。定位为学习/求职项目，核心目标是掌握 RAG、Embedding、Agent、向量检索等 AI 工程能力。

---

## 二、技术选型（已确认）

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 基础设施 | Docker Compose 全部容器化 | 学习 Docker 编排，接近生产环境 |
| 后端架构 | 单体 FastAPI + Router 分层 | 先跑通核心流程，后续可拆 |
| LLM 方案 | 抽象层，支持云端 API 和本地 Ollama | 学习 LLM 抽象设计，开发时用云端验证 |
| 文档处理 | 同步处理先行 | 先理解每步逻辑，稳定后迁移异步 |
| 前端 | 最小可用 Chat UI | 验证 RAG 效果即可，非核心学习重点 |
| 数据库 | PostgreSQL + Redis + Qdrant | 企业标配三件套 |
| 开发语言 | Python + FastAPI | AI/RAG 生态事实标准 |

---

## 三、系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│        Chat UI ─── API Client ─── 知识库选择器           │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────┐
│                  Backend (FastAPI)                       │
│                                                         │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  │
│  │ Auth    │  │ 知识库    │  │ 文档    │  │ Chat     │  │
│  │ Router  │  │ Router   │  │ Router  │  │ Router   │  │
│  └────┬────┘  └────┬─────┘  └────┬────┘  └────┬─────┘  │
│       │            │             │             │        │
│  ┌────▼────────────▼─────────────▼─────────────▼─────┐  │
│  │               Services 层 (业务逻辑)              │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │                               │
│  ┌──────────────────────▼────────────────────────────┐  │
│  │        RAG Pipeline                               │  │
│  │  Query Rewrite → Embedding → Search → Rerank      │  │
│  │  → Context Compression → Prompt → LLM → Answer    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────┐  ┌────────────────────────────────┐  │
│  │ LLM 抽象层    │  │ Document Pipeline              │  │
│  │ Cloud / Ollama │  │ Parse → Chunk → Vectorize     │  │
│  └───────────────┘  └────────────────────────────────┘  │
└─────────┬──────────────┬──────────────────┬─────────────┘
          │              │                  │
    ┌─────▼─────┐  ┌─────▼─────┐   ┌───────▼───────┐
    │ PostgreSQL │  │  Redis    │   │    Qdrant     │
    │ 业务数据   │  │ 缓存/队列 │   │  向量存储     │
    └───────────┘  └───────────┘   └───────────────┘
```

---

## 四、数据库职责划分

### PostgreSQL — 主业务数据库

| 数据 | 说明 |
|------|------|
| 用户 | 账号、密码哈希、角色 |
| 知识库 | 名称、描述、Embedding 模型配置 |
| 文档元数据 | 文件名、路径、大小、状态（uploading → parsing → chunking → vectorizing → done/failed） |
| 文本片段 | 内容、切片序号、元数据（文件名、页码、来源） |
| 对话 | 会话标题、关联知识库 |
| 消息 | 角色（user/assistant）、内容、引用来源 |

不存：向量、缓存、原始文件

### Redis — 高速缓存与队列

| 用途 | Key 格式 | 说明 |
|------|----------|------|
| Session | `session:{user_id}` | JWT token 缓存 |
| API 限流 | `ratelimit:{ip}:{minute}` | 请求计数 |
| 热门问答缓存 | `cache:{query_hash}` | 第二阶段 |
| 异步任务队列 | `queue:documents` | 第二阶段 |

不存：持久业务数据

### Qdrant — 向量存储

| 项目 | 说明 |
|------|------|
| Collection | `kb_{knowledge_base_id}`，每个知识库独立集合 |
| 向量维度 | 1024（BGE-Large）或 384（BGE-Small） |
| Payload | chunk_id、document_id、filename、page、content |
| 检索方式 | Dense Search，后续扩展 Hybrid Search |

不存：业务元数据、原始文档

---

## 五、目录结构

```
enterprise_rag_system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理（环境变量）
│   │   ├── database.py          # SQLAlchemy 引擎和 Session
│   │   ├── api/
│   │   │   ├── auth.py          # 认证路由
│   │   │   ├── knowledge_base.py # 知识库 CRUD
│   │   │   ├── document.py      # 文档上传/管理
│   │   │   └── chat.py          # RAG 聊天
│   │   ├── models/              # SQLAlchemy ORM 模型
│   │   ├── services/            # 业务逻辑
│   │   ├── rag/
│   │   │   ├── pipeline.py      # RAG 流水线编排
│   │   │   ├── retriever.py     # 向量检索
│   │   │   └── generator.py     # LLM 生成
│   │   ├── llm/
│   │   │   ├── base.py          # LLM 抽象接口
│   │   │   ├── ollama.py        # Ollama 实现
│   │   │   └── openai.py        # 云端 API 实现
│   │   ├── embeddings/          # 文本向量化
│   │   ├── vectorstore/         # Qdrant 集成
│   │   └── utils/               # 工具函数
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/                     # Next.js 页面
│   ├── components/              # React 组件
│   ├── lib/                     # API 客户端
│   └── package.json
├── docker-compose.yml
├── .env.example
└── docs/                        # 学习文档输出目录
```

---

## 六、核心 RAG 流程

```
用户提问
  │
  ▼
┌──────────────┐
│ Query Rewrite│  改写用户问题，提升检索质量（第一版跳过）
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Embedding   │  将问题文本转为向量（BGE 模型）
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Qdrant 检索  │  向量相似度搜索，返回 Top-K 结果
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Rerank     │  重排序（第一版跳过）
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Context 压缩 │  简单截断，控制 Token 数
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Prompt 构建  │  检索结果注入 System Prompt 模板
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  LLM 生成    │  通过抽象层调用 Cloud/Ollama
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 返回回答     │  answer + sources（引用来源）
└──────────────┘
```

第一版最小闭环：**Embedding → 检索 → Prompt 构建 → LLM 生成**。

---

## 七、LLM 抽象层设计

```python
# 接口定义（伪代码）
class BaseLLM(ABC):
    async def generate(prompt: str, context: str) -> str: ...

class OllamaLLM(BaseLLM):
    # 调用本地 Ollama API

class OpenAILLM(BaseLLM):
    # 调用云端 OpenAI/Claude API
```

通过配置切换实现，业务代码不感知具体 LLM 供应商。

---

## 八、开发阶段

| Step | 内容 | 学习重点 |
|------|------|---------|
| 1 | 项目骨架：Docker Compose、FastAPI 脚手架、数据库连接 | Docker 编排、FastAPI 基础、SQLAlchemy |
| 2 | 用户系统：注册/登录/JWT 鉴权 | 认证、JWT、Pydantic |
| 3 | 知识库 + 文档管理：CRUD、文件上传 | RESTful API、文件处理 |
| 4 | 文档处理流水线：解析 → 切片 → 向量化 → 入库 | PDF 解析、Embedding、Qdrant |
| 5 | RAG 最小闭环：检索 + Prompt + LLM 生成 | RAG 核心、Prompt 工程、LLM 调用 |
| 6 | Chat UI：前端对话界面 | Next.js、React、API 对接 |
| 7 | 学习文档输出 | 知识沉淀 |

---

## 九、学习文档产出要求

每个 Step 完成后生成一份教学文档，内容包括：

1. **完成了什么** — 本阶段实现的功能概述
2. **使用了什么技术** — 技术栈列表和选型理由
3. **技术知识点** — 每项技术的核心概念讲解
4. **对应项目模块** — 这些技术应用在项目的哪个部分

文档以教学风格撰写，适合后续复习和知识沉淀。同步写入 Obsidian 笔记库。

---

## 十、API 接口设计

### 认证

- `POST /api/auth/register` — 用户注册（username, email, password）
- `POST /api/auth/login` — 用户登录，返回 JWT

### 知识库

- `POST /api/kb/create` — 创建知识库
- `GET /api/kb/list` — 获取知识库列表
- `GET /api/kb/{id}` — 获取知识库详情
- `DELETE /api/kb/{id}` — 删除知识库

### 文档

- `POST /api/document/upload` — 上传文档（multipart/form-data）
- `GET /api/document/list?kb_id=` — 获取文档列表
- `DELETE /api/document/{id}` — 删除文档

### 聊天

- `POST /api/chat` — 发送消息（kb_id, message, chat_id?）
- `GET /api/chat/history?chat_id=` — 获取聊天记录

### 健康检查

- `GET /health` — 服务健康检查
- `GET /api/v1/health` — API v1 健康检查

---

## 十一、推荐模型

| 模型 | 用途 | 说明 |
|------|------|------|
| Qwen 14B | 问答生成 | 通过 Ollama 本地部署 |
| DeepSeek R1 | 复杂推理 | 通过 Ollama 本地部署 |
| BGE-Large | 文本向量化 | 1024 维，中文效果好 |
| BGE-Small | 文本向量化（轻量） | 384 维，速度快 |

开发阶段可通过云端 API（OpenAI/Claude）替代，通过 LLM 抽象层切换。

---

## 十二、Docker Compose 服务清单

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| postgres | postgres:16 | 5432 | 主数据库 |
| redis | redis:7-alpine | 6379 | 缓存/队列 |
| qdrant | qdrant/qdrant | 6333 | 向量数据库 |
| ollama | ollama/ollama | 11434 | LLM 推理 |
| backend | 自建 | 8000 | FastAPI 后端 |
| frontend | 自建 | 3000 | Next.js 前端 |
