from app.llm.factory import get_llm
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer


async def run_rag(kb_id: int, question: str) -> dict:
    """RAG 流水线：检索 → 生成"""
    chunks = retrieve(kb_id, question, top_k=5)
    llm = get_llm()
    result = await generate_answer(llm, chunks, question)
    return result
