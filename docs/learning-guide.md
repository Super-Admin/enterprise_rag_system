---
title: 企业 RAG 系统学习指南
date: 2026-05-29
tags: [学习, 面试, RAG, AI工程]
---

# 企业 RAG 系统学习指南

## 一、核心架构亮点

| 技术点 | 面试表述 | 难度 |
|--------|----------|------|
| **RAG 流水线** | 实现了完整的检索增强生成流程：查询改写→向量化→检索→重排序→上下文压缩→生成 | ⭐⭐⭐⭐ |
| **向量数据库** | 使用 Qdrant 进行高性能相似度检索，支持 512 维 BGE embedding | ⭐⭐⭐ |
| **异步文档处理** | 线程池架构实现非阻塞上传，避免 API 请求阻塞 | ⭐⭐⭐ |
| **LLM 集成** | 支持 Ollama 本地推理和 OpenAI API，实现混合部署 | ⭐⭐⭐ |

---

## 二、关键技术点详解

### 1. RAG 流水线设计

```
用户提问 → 查询改写 → Embedding → Qdrant 检索 → Rerank → 上下文压缩 → LLM 生成 → 引用来源
```

**面试亮点：**
- 为什么需要查询改写？（提升检索准确率）
- Rerank 的作用？（向量检索是近似匹配，Rerank 用语义模型精排）
- 上下文压缩？（减少 token 消耗，提升相关性）

### 2. 向量检索优化

- BGE 模型：中文优化的 512 维 embedding
- Qdrant：支持过滤、payload 存储、批量操作
- 相似度算法：余弦相似度（COSINE）

**面试亮点：**
- 为什么选 BGE 而不是 OpenAI embedding？（中文优化、本地部署、零成本）
- Qdrant vs Milvus vs Weaviate？（轻量级、Docker 友好）

### 3. 异步文档处理

```python
# 线程池实现
thread = threading.Thread(target=process_in_background, args=(doc.id,))
thread.daemon = True
thread.start()
```

**面试亮点：**
- 为什么用线程池而不用 Celery？（简单场景、减少依赖）
- 状态追踪：uploading → parsing → chunking → vectorizing → done/failed
- 错误处理：error_message 字段记录失败原因

### 4. 认证与安全

- JWT 认证：24 小时过期
- RBAC 权限：admin/user/guest 角色
- 文件权限：用户只能访问自己的知识库

**面试亮点：**
- JWT vs Session？（无状态、适合微服务）
- 如何防止 Prompt Injection？（输入过滤、系统提示词约束）

---

## 三、技术栈深度

| 组件 | 技术深度 |
|------|----------|
| **FastAPI** | 异步路由、依赖注入、Pydantic 验证、中间件 |
| **SQLAlchemy** | ORM 模型、关系映射、Session 管理 |
| **Qdrant** | Collection 管理、向量检索、Payload 过滤 |
| **Ollama** | 本地 LLM 推理、超时处理、错误重试 |
| **Next.js** | App Router、Server Components、Client Components |

---

## 四、面试高频问题

### 1. RAG 相关

**Q: 为什么用 RAG 而不是微调？**
A: RAG 知识可更新、无需训练成本、可解释性强（有引用来源）

**Q: 如何提升 RAG 检索准确率？**
A: 查询改写 + Rerank 重排序 + 上下文压缩 + 混合检索（向量+关键词）

**Q: 向量数据库选型考虑？**
A: 性能、扩展性、运维成本、社区生态。Qdrant 轻量级适合中小规模

### 2. 工程实践

**Q: 如何处理大文件上传？**
A: 异步处理、状态追踪、错误重试、文件大小限制（50MB）

**Q: 如何保证数据一致性？**
A: 删除文档时同步清理 Qdrant 向量 + PostgreSQL chunks 表

**Q: 如何优化 LLM 推理性能？**
A: 本地部署（Ollama）减少网络延迟、超时处理（300s）、Prompt 压缩

### 3. 系统设计

**Q: 如何设计企业级知识库系统？**
A: 分层架构（API→Service→Data）、异步处理、权限控制、多格式支持

**Q: 如何处理多用户并发？**
A: 数据库连接池、异步 IO、用户级隔离（知识库权限）

---

## 五、项目亮点总结

**技术深度：**
- 完整 RAG 流水线实现
- 向量数据库深度使用
- LLM 本地部署与优化

**工程实践：**
- 异步处理与状态追踪
- 错误处理与日志记录
- 测试覆盖（100%）

**架构设计：**
- 分层架构清晰
- 组件解耦
- 可扩展性强

---

## 六、简历描述建议

```
企业知识库 RAG 系统 | 技术栈：FastAPI + Qdrant + Ollama + Next.js
• 实现完整 RAG 流水线：文档解析→向量化→检索→重排序→生成
• 使用 Qdrant 向量数据库，支持 512 维 BGE embedding 相似度检索
• 设计异步文档处理架构，支持 PDF/DOCX/MD/TXT 多格式上传
• 集成 Ollama 本地 LLM 推理，实现零成本 AI 问答
• 100% 测试覆盖，包含 28 个测试用例
```

---

## 七、学习路线图

### 第一阶段：基础掌握（1-2 周）
- [ ] 理解 RAG 基本概念和流程
- [ ] 掌握 FastAPI 框架和异步编程
- [ ] 了解向量数据库原理（Qdrant/Milvus）
- [ ] 熟悉 SQLAlchemy ORM

### 第二阶段：深入理解（2-3 周）
- [ ] RAG 优化技巧（查询改写、Rerank、上下文压缩）
- [ ] LLM 集成与 Prompt 工程
- [ ] 向量检索算法（余弦相似度、HNSW）
- [ ] 系统架构设计模式

### 第三阶段：实战应用（3-4 周）
- [ ] 完整项目开发经验
- [ ] 性能优化与调优
- [ ] 测试与质量保证
- [ ] 部署与运维

---

## 八、问题记录区

### 问题 1：
**问题描述：**


**解决方案：**


**学习收获：**


---

### 问题 2：
**问题描述：**


**解决方案：**


**学习收获：**


---

### 问题 3：
**问题描述：**


**解决方案：**


**学习收获：**

---

## 九、参考资料

- [RAG 论文原文](https://arxiv.org/abs/2005.11401)
- [Qdrant 官方文档](https://qdrant.tech/documentation/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [BGE 模型](https://huggingface.co/BAAI/bge-small-zh-v1.5)
