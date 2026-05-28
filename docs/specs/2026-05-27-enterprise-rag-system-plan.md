# 企业知识库 RAG 系统 — 实施计划书

> 日期：2026-05-27
> 配套设计文档：`docs/specs/2026-05-27-enterprise-rag-system-design.md`

---

## 总览

| Step | 内容 | 预计产出 | 学习文档 |
|------|------|---------|---------|
| 1 | 项目骨架 | Docker Compose + FastAPI 脚手架 + 数据库连接 | Docker/FastAPI/SQLAlchemy |
| 2 | 用户系统 | 注册/登录/JWT 鉴权 | 认证/JWT/Pydantic |
| 3 | 知识库 + 文档管理 | CRUD + 文件上传 | RESTful API/文件处理 |
| 4 | 文档处理流水线 | 解析 → 切片 → 向量化 → 入库 | PDF 解析/Embedding/Qdrant |
| 5 | RAG 最小闭环 | 检索 + Prompt + LLM 生成 | RAG/Prompt 工程/LLM 调用 |
| 6 | Chat UI | 前端对话界面 | Next.js/React/API 对接 |
| 7 | 学习文档输出 | Obsidian 教学文档 | 知识沉淀 |

---

## Step 1：项目骨架

### 目标

搭建可运行的开发环境，启动所有基础服务，验证前后端连通。

### 任务清单

#### 1.1 Docker Compose 配置

- 创建 `docker-compose.yml`，包含 6 个服务：
  - `postgres`：postgres:16，端口 5432，挂载数据卷，配置环境变量
  - `redis`：redis:7-alpine，端口 6379
  - `qdrant`：qdrant/qdrant，端口 6333，挂载数据卷
  - `ollama`：ollama/ollama，端口 11434，挂载模型卷
  - `backend`：自建 Dockerfile，端口 8000，依赖 postgres/redis/qdrant
  - `frontend`：自建 Dockerfile，端口 3000，依赖 backend
- 创建 `.env.example`，列出所有环境变量模板
- 验证：`docker compose up -d` 全部服务启动无报错

#### 1.2 FastAPI 后端脚手架

- 创建 `backend/` 目录结构：
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py           # FastAPI 入口，挂载路由
  │   ├── config.py          # Pydantic Settings 管理环境变量
  │   └── database.py        # SQLAlchemy engine + SessionLocal
  ├── requirements.txt
  ├── Dockerfile
  └── .env.example
  ```
- `main.py`：创建 FastAPI 实例，挂载 `/health` 和 `/api/v1/health` 路由
- `config.py`：使用 `pydantic-settings` 读取 `.env` 配置（DATABASE_URL, REDIS_URL, QDRANT_URL 等）
- `database.py`：SQLAlchemy `create_engine` + `sessionmaker`，提供 `get_db` 依赖注入
- `requirements.txt`：fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic-settings, python-dotenv
- 验证：`uvicorn app.main:app --reload` 启动，访问 `/docs` 看到 Swagger UI

#### 1.3 Next.js 前端脚手架

- 使用 `npx create-next-app@latest frontend` 初始化（TypeScript + TailwindCSS + App Router）
- 创建 `frontend/Dockerfile`
- 验证：`npm run dev` 启动，访问 http://localhost:3000

#### 1.4 数据库初始化

- 创建 SQLAlchemy 基础模型（`Base = declarative_base()`）
- 编写 Alembic 初始化命令（或手动 `Base.metadata.create_all`）
- 验证：连接 PostgreSQL，建表成功

#### 1.5 项目根目录文件

- `.gitignore`：Python、Node、Docker 相关忽略规则
- `.env.example`：所有环境变量模板
- 更新 `CLAUDE.md`：补充实际开发命令

### 验收标准

- [ ] `docker compose up -d` 启动全部服务
- [ ] http://localhost:8000/docs 可访问 Swagger UI
- [ ] http://localhost:8000/health 返回 200
- [ ] http://localhost:3000 可访问前端页面
- [ ] PostgreSQL 连接成功，可建表

---

## Step 2：用户系统

### 目标

实现用户注册、登录、JWT 鉴权，为后续接口提供认证基础。

### 任务清单

#### 2.1 数据模型

- 创建 `app/models/user.py`：
  - `User` 模型：id, username, email, password_hash, role, created_at, updated_at
  - 使用 `bcrypt` 哈希密码
- 创建 `app/models/__init__.py`，统一导出

#### 2.2 Pydantic Schema

- 创建 `app/schemas/user.py`：
  - `UserCreate`：username, email, password（注册请求）
  - `UserLogin`：email, password（登录请求）
  - `UserResponse`：id, username, email, role（响应，不含密码）
  - `Token`：access_token, token_type（JWT 响应）

#### 2.3 认证服务

- 创建 `app/services/auth.py`：
  - `register(user_data)` → 创建用户，返回 UserResponse
  - `login(credentials)` → 验证密码，返回 JWT Token
  - `get_current_user(token)` → 解析 JWT，返回当前用户
- JWT 使用 `python-jose` 库，配置过期时间

#### 2.4 认证路由

- 创建 `app/api/auth.py`：
  - `POST /api/auth/register` → 注册
  - `POST /api/auth/login` → 登录
  - `GET /api/auth/me` → 获取当前用户信息（需认证）
- 创建 `app/api/deps.py`：`get_current_user` 依赖注入

#### 2.5 中间件

- CORS 中间件配置（允许前端跨域）

### 验收标准

- [ ] POST /api/auth/register 成功创建用户
- [ ] POST /api/auth/login 返回 JWT Token
- [ ] 带 Token 访问 /api/auth/me 返回用户信息
- [ ] 无 Token 访问受保护接口返回 401
- [ ] Swagger UI 中可直接测试认证流程

---

## Step 3：知识库 + 文档管理

### 目标

实现知识库和文档的 CRUD，支持文件上传。

### 任务清单

#### 3.1 数据模型

- `KnowledgeBase`：id, user_id, name, description, embedding_model, created_at
- `Document`：id, kb_id, filename, file_path, file_size, status, created_at
  - status 枚举：uploading, parsing, chunking, vectorizing, done, failed

#### 3.2 Schema + Service + Router

- 知识库：create, list, get, delete
- 文档：upload（multipart/form-data）, list, delete
- 文件存储到 `backend/uploads/` 目录
- 文档上传后 status 设为 `uploading`

#### 3.3 文件上传实现

- 使用 FastAPI 的 `UploadFile` + `shutil` 保存文件
- 校验文件类型（PDF, DOCX, TXT, MD）
- 校验文件大小（限制可配置）

### 验收标准

- [ ] 创建/列表/删除知识库正常
- [ ] 上传文档到指定知识库正常
- [ ] 文档状态显示正确
- [ ] 文件保存到指定目录

---

## Step 4：文档处理流水线

### 目标

实现文档解析 → 切片 → 向量化 → 入库的完整链路。

### 任务清单

#### 4.1 文档解析

- 创建 `app/services/document_parser.py`：
  - PDF 解析：`pymupdf` 或 `pdfplumber`
  - DOCX 解析：`python-docx`
  - TXT/MD 解析：直接读取
  - 统一输出：文本内容 + 页码/位置元数据

#### 4.2 文本切片

- 创建 `app/services/chunker.py`：
  - 按字符数切片（默认 chunk_size=500, overlap=50）
  - 保留元数据：filename, page, chunk_index
  - 输出：`[{content, metadata}]`

#### 4.3 Embedding 服务

- 创建 `app/embeddings/bge.py`：
  - 使用 `sentence-transformers` 加载 BGE 模型
  - `embed_texts(texts: list[str]) → list[list[float]]`
  - 支持批量向量化

#### 4.4 Qdrant 集成

- 创建 `app/vectorstore/qdrant_client.py`：
  - `create_collection(kb_id, vector_size)` → 创建集合
  - `upsert_chunks(kb_id, chunks, vectors)` → 写入向量 + payload
  - `search(kb_id, query_vector, top_k)` → 相似度检索

#### 4.5 文档处理 Service

- 创建 `app/services/document_processor.py`：
  - `process_document(document_id)`：
    1. 更新状态 → parsing
    2. 解析文档
    3. 更新状态 → chunking
    4. 文本切片
    5. 更新状态 → vectorizing
    6. 生成 Embedding
    7. 写入 Qdrant + PostgreSQL chunks 表
    8. 更新状态 → done
- 上传文档后自动触发处理

#### 4.6 Chunk 数据模型

- `Chunk`：id, document_id, content, chunk_index, metadata, created_at

### 验收标准

- [ ] 上传 PDF 后自动解析、切片、向量化
- [ ] chunks 表有数据
- [ ] Qdrant 集合中有向量数据
- [ ] 文档状态最终变为 done（或失败时为 failed）
- [ ] 向量检索能返回结果

---

## Step 5：RAG 最小闭环

### 目标

用户提问 → 检索相关文档 → LLM 生成带引用的回答。

### 任务清单

#### 5.1 LLM 抽象层

- 创建 `app/llm/base.py`：
  ```python
  class BaseLLM(ABC):
      async def generate(self, prompt: str) -> str: ...
  ```
- 创建 `app/llm/ollama.py`：调用 Ollama HTTP API
- 创建 `app/llm/openai.py`：调用 OpenAI 兼容 API
- 创建 `app/llm/factory.py`：根据配置返回对应实现

#### 5.2 RAG 流水线

- 创建 `app/rag/retriever.py`：
  - 接收用户问题
  - 调用 Embedding 服务生成问题向量
  - 调用 Qdrant 检索 Top-K 结果
  - 返回 chunks + score
- 创建 `app/rag/generator.py`：
  - 构建 System Prompt（注入检索到的上下文）
  - 调用 LLM 生成回答
  - 附带引用来源
- 创建 `app/rag/pipeline.py`：
  - 编排 retriever + generator
  - 输入：question + kb_id
  - 输出：answer + sources

#### 5.3 Prompt 模板

- 创建 `app/prompts/templates.py`：
  ```
  你是一个企业知识库助手。基于以下参考资料回答用户问题。
  如果参考资料中没有相关信息，请明确说明。

  参考资料：
  {context}

  用户问题：{question}
  ```

#### 5.4 Chat 路由

- 创建 `app/api/chat.py`：
  - `POST /api/chat` → 调用 RAG pipeline，返回 answer + sources
  - `GET /api/chat/history` → 查询消息记录
- 数据模型：`Chat`, `Message`

### 验收标准

- [ ] 上传一个 PDF 文档，完成向量化
- [ ] 提问与文档内容相关的问题，返回正确回答
- [ ] 回答附带引用来源（文档名、页码）
- [ ] LLM 抽象层可通过配置切换 Cloud/Ollama
- [ ] Swagger UI 中可完整测试 RAG 流程

---

## Step 6：Chat UI

### 目标

搭建最小可用的前端对话界面。

### 任务清单

#### 6.1 页面结构

- `/` — 主页，包含知识库选择器和聊天区
- 聊天区：消息列表 + 输入框

#### 6.2 组件

- `KnowledgeBaseSelector` — 下拉选择知识库
- `ChatMessage` — 单条消息展示（区分 user/assistant）
- `ChatInput` — 输入框 + 发送按钮
- `SourceCard` — 引用来源展示

#### 6.3 API 客户端

- 创建 `lib/api.ts`：
  - `fetchKnowledgeBases()`
  - `sendMessage(kbId, message)`
  - `fetchChatHistory(chatId)`

#### 6.4 交互流程

- 选择知识库 → 输入问题 → 发送 → 显示回答 + 引用来源
- 消息列表自动滚动到最新
- 加载状态展示

### 验收标准

- [ ] 页面正常渲染
- [ ] 可选择知识库
- [ ] 发送消息后收到 RAG 回答
- [ ] 引用来源正确展示
- [ ] 前后端连通

---

## Step 7：学习文档输出

### 目标

为每个 Step 生成教学文档，同步到 Obsidian 笔记库。

### 任务清单

- 为 Step 1~6 各生成一份文档，包含：
  1. 完成了什么（功能概述）
  2. 使用了什么技术（技术栈 + 选型理由）
  3. 技术知识点（核心概念讲解，带代码示例）
  4. 对应项目模块（技术 → 代码文件的映射）
- 文档写入 Obsidian vault 对应目录
- 建立索引页，串联所有学习文档

### 验收标准

- [ ] 6 份学习文档全部生成
- [ ] 写入 Obsidian vault
- [ ] 索引页可导航到各文档

---

## 依赖关系

```
Step 1 (骨架)
  └── Step 2 (用户系统)
        └── Step 3 (知识库 + 文档)
              └── Step 4 (文档处理)
                    └── Step 5 (RAG 闭环)
                          └── Step 6 (Chat UI)
                                └── Step 7 (学习文档)
```

每个 Step 依赖前一个 Step 完成。Step 7 汇总所有前序 Step 的学习内容。

---

## 关键依赖库

### Python (requirements.txt)

```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
pydantic-settings
python-dotenv
python-jose[cryptography]    # JWT
passlib[bcrypt]              # 密码哈希
python-multipart             # 文件上传
pymupdf                      # PDF 解析
python-docx                  # DOCX 解析
sentence-transformers        # BGE Embedding
qdrant-client                # Qdrant SDK
httpx                        # HTTP 客户端（调用 Ollama）
openai                       # OpenAI 兼容 API
```

### Node.js (package.json)

```
next
react
react-dom
tailwindcss
@radix-ui/react-*            # shadcn/ui 依赖
```
