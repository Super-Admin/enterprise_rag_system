# 企业知识库 RAG 系统需求文档（AI 工程实战项目）

# 一、项目背景

随着大模型技术的发展，越来越多企业希望能够：

- 基于企业内部知识构建 AI 问答系统
- 让 AI 理解企业文档
- 提供企业级知识检索能力
- 实现智能客服 / 内部助手 / 技术助手
- 降低知识查找成本

因此需要构建一个：

# 企业级 AI 知识库 RAG 系统

该系统需要支持：

- 文档上传
- 文档解析
- 向量化存储
- 智能检索
- 多轮对话
- Agent Tool 调用
- 权限控制
- AI 问答

本项目目标并非 Demo，而是：

# 按真实 AI 工程系统进行设计

用于：

- AI 工程学习
- 求职项目
- 技术栈提升
- AI 工程化实践

---

# 二、项目目标

实现一个完整的企业知识库 AI 系统。

用户能够：

- 上传 PDF / Word / Markdown 等文档
- 自动解析内容
- 自动构建向量知识库
- 基于 RAG 进行问答
- 进行多轮对话
- 调用 Agent Tool
- 管理不同知识库
- 管理用户权限

---

# 三、项目核心价值

本项目将帮助学习并掌握：

## AI 工程能力

- RAG
- Embedding
- Rerank
- Context Engineering
- Prompt Engineering
- Agent
- MCP
- Tool Calling

## 后端工程能力

- FastAPI
- 微服务思想
- 异步任务
- Redis
- PostgreSQL
- Docker

## AI Infra 能力

- Ollama
- Qdrant
- 本地模型部署
- 向量数据库
- 模型服务化

## 前端能力

- React
- Next.js
- AI Chat UI

---

# 四、技术架构

# 后端技术栈

| 技术 | 用途 |
|---|---|
| Python | 主开发语言 |
| FastAPI | Web API |
| SQLAlchemy | ORM |
| PostgreSQL | 主数据库 |
| Redis | 缓存 / Session / Queue |
| Celery / RQ | 异步任务 |
| Docker | 容器化 |

---

# AI 技术栈

| 技术 | 用途 |
|---|---|
| LangChain | RAG 与 Agent |
| LangGraph | Workflow |
| Ollama | 本地模型 |
| Qdrant | 向量数据库 |
| BGE Embedding | 文本向量化 |
| Rerank Model | 检索优化 |

---

# 前端技术栈

| 技术 | 用途 |
|---|---|
| React | UI |
| Next.js | 前端框架 |
| TailwindCSS | 样式 |
| shadcn/ui | 组件 |

---

# 五、系统架构设计

# 系统模块

## 1. 用户系统

负责：

- 用户登录
- 用户注册
- Token 鉴权
- 权限管理
- 团队管理

---

## 2. 知识库系统

负责：

- 创建知识库
- 管理知识库
- 文档管理
- 文档删除
- 文档状态管理

---

## 3. 文档解析系统

负责：

- PDF 解析
- Markdown 解析
- DOCX 解析
- 文本提取
- OCR（后续可扩展）

---

## 4. Chunk 切分系统

负责：

- 文本切片
- Chunk 优化
- Overlap
- Metadata 管理

---

## 5. Embedding 系统

负责：

- 文本向量化
- 向量缓存
- Batch Embedding
- Embedding 管理

---

## 6. 向量检索系统

负责：

- 向量召回
- Hybrid Search
- Metadata Filter
- TopK 搜索

---

## 7. Rerank 系统

负责：

- 重排序
- 提升召回质量
- Context 优化

---

## 8. RAG 问答系统

负责：

- Prompt 构建
- Context 注入
- 问答生成
- 引用来源

---

## 9. 多轮对话系统

负责：

- Chat History
- Session Memory
- 上下文管理
- Token 控制

---

## 10. Agent Tool 系统

负责：

- Tool Calling
- SQL Tool
- Browser Tool
- Search Tool
- 文件 Tool

---

# 六、系统功能需求

# 1. 用户模块

## 功能

### 用户注册

支持：

- 用户名
- 邮箱
- 密码

---

### 用户登录

支持：

- JWT 登录
- Token 刷新
- Session 管理

---

### 权限控制

角色：

- 管理员
- 普通用户
- 访客

---

# 2. 知识库模块

## 功能

### 创建知识库

字段：

- 知识库名称
- 描述
- 权限
- Embedding Model
- Rerank Model

---

### 文档上传

支持格式：

- PDF
- DOCX
- TXT
- Markdown

---

### 文档状态

状态包括：

- 上传中
- 解析中
- 向量化中
- 完成
- 失败

---

# 3. 文档解析模块

## 功能

### PDF 解析

使用：

- pymupdf
- pdfplumber

---

### 文档切片

需要支持：

- chunk_size
- overlap
- metadata

---

### Metadata

必须保存：

- 文件名
- 页码
- chunk_id
- source
- user_id

---

# 4. 向量检索模块

## 功能

### Embedding

使用：

- BGE Small
- BGE Large

---

### 向量存储

使用：

- Qdrant

---

### 检索模式

支持：

- Dense Search
- Hybrid Search
- Metadata Filter

---

# 5. RAG 问答模块

## 功能

### AI 对话

支持：

- 多轮对话
- 引用来源
- Context Injection
- 历史记录

---

### Prompt 管理

支持：

- System Prompt
- Template Prompt
- Dynamic Prompt

---

### 回答优化

支持：

- Rerank
- Context Compression
- TopK

---

# 6. Agent Tool 模块

## 第一阶段

支持：

- 文件查询 Tool
- 搜索 Tool
- SQL Tool

---

## 第二阶段

支持：

- Browser Tool
- MCP Tool
- API Tool

---

# 七、数据库设计

# 核心表

## users

字段：

- id
- username
- email
- password_hash
- role
- created_at

---

## knowledge_bases

字段：

- id
- user_id
- name
- description
- embedding_model
- created_at

---

## documents

字段：

- id
- kb_id
- filename
- status
- file_size
- created_at

---

## chunks

字段：

- id
- document_id
- content
- chunk_index
- metadata

---

## chats

字段：

- id
- user_id
- kb_id
- title
- created_at

---

## messages

字段：

- id
- chat_id
- role
- content
- created_at

---

# 八、API 设计

# 用户接口

## POST /api/auth/register

用户注册。

---

## POST /api/auth/login

用户登录。

---

# 知识库接口

## POST /api/kb/create

创建知识库。

---

## GET /api/kb/list

获取知识库列表。

---

## DELETE /api/kb/{id}

删除知识库。

---

# 文档接口

## POST /api/document/upload

上传文档。

---

## GET /api/document/list

获取文档列表。

---

# Chat 接口

## POST /api/chat

发送消息。

---

## GET /api/chat/history

获取聊天记录。

---

# 九、RAG 核心流程

# 流程图

用户提问
↓
Query Rewrite
↓
Embedding
↓
Qdrant 检索
↓
Rerank
↓
Context Compression
↓
Prompt 构建
↓
LLM 推理
↓
生成回答
↓
返回引用来源

---

# 十、系统目录结构

```text
backend/
 ├── app/
 │   ├── api/
 │   ├── models/
 │   ├── services/
 │   ├── rag/
 │   ├── agents/
 │   ├── embeddings/
 │   ├── vectorstore/
 │   ├── prompts/
 │   ├── tasks/
 │   └── utils/
 │
 ├── docker/
 ├── scripts/
 └── requirements.txt

frontend/
 ├── app/
 ├── components/
 ├── hooks/
 ├── lib/
 └── services/
```

---

# 十一、部署方案

# Docker Compose

服务包括：

- backend
- frontend
- postgres
- redis
- qdrant
- ollama

---

# 本地模型

推荐：

| 模型 | 用途 |
|---|---|
| Qwen 14B | 问答 |
| DeepSeek R1 | 推理 |
| BGE | Embedding |

---

# 十二、性能优化

# 检索优化

包括：

- Hybrid Search
- Rerank
- Query Rewrite
- Chunk 优化

---

# Token 优化

包括：

- Context Compression
- Sliding Window
- Summarization Memory

---

# 十三、安全设计

# 必须支持

- JWT
- RBAC
- 文件权限
- API 限流
- Prompt Injection 防护

---

# 十四、项目阶段规划

# 第一阶段（基础版）

目标：

完成：

- 文档上传
- 向量化
- RAG 问答
- Chat UI

预计：2~3周

---

# 第二阶段（进阶版）

目标：

完成：

- 多轮对话
- Rerank
- Redis Cache
- Prompt 优化

预计：2周

---

# 第三阶段（高级版）

目标：

完成：

- Agent Tool
- SQL Tool
- Browser Tool
- Workflow

预计：3~4周

---

# 第四阶段（企业版）

目标：

完成：

- 多用户
- 权限系统
- MCP Tool
- 多 Agent
- Kubernetes 部署

预计：长期演进

---

# 十五、项目学习目标

完成本项目后，应掌握：

# AI 工程能力

- RAG
- Embedding
- Rerank
- Agent
- Workflow
- MCP
- Tool Calling

---

# 后端能力

- FastAPI
- Redis
- PostgreSQL
- Docker
- 异步任务

---

# AI Infra 能力

- Ollama
- Qdrant
- 本地模型部署
- 模型服务化

---

# 十六、最终项目效果

最终应达到：

- 可实际运行
- 可多人使用
- 支持企业知识库
- 支持 AI 问答
- 支持 Agent Tool
- 支持本地模型
- 支持 Docker 一键部署

并能够作为：

- AI 工程师求职项目
- GitHub 核心项目
- AI 工程学习案例
- 企业 AI 系统 Demo

使用。

