from app.llm.base import BaseLLM

SYSTEM_PROMPT = """你是一个企业知识库助手。基于以下参考资料回答用户问题。
如果参考资料中没有相关信息，请明确说明。
回答时请引用来源（文件名和页码）。"""


def build_prompt(context: str, question: str) -> str:
    return f"""{SYSTEM_PROMPT}

参考资料：
{context}

用户问题：{question}

请基于参考资料回答："""


def format_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("filename", "未知")
        page = chunk.get("page", 1)
        content = chunk.get("content", "")
        parts.append(f"[{i}] 来源: {source} (第{page}页)\n{content}")
    return "\n\n".join(parts)


async def generate_answer(llm: BaseLLM, chunks: list[dict], question: str) -> dict:
    """生成回答"""
    context = format_context(chunks)
    prompt = build_prompt(context, question)
    answer = await llm.generate(prompt)

    sources = [
        {
            "filename": c.get("filename", ""),
            "page": c.get("page", 1),
            "score": c.get("score", 0),
        }
        for c in chunks
    ]

    return {"answer": answer, "sources": sources}
