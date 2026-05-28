from app.embeddings.bge import embed_texts
from app.vectorstore.qdrant_client import search


def retrieve(kb_id: int, query: str, top_k: int = 5) -> list[dict]:
    """检索相关文档片段"""
    try:
        query_vector = embed_texts([query])[0]
        results = search(kb_id, query_vector, top_k=top_k)
        return results
    except Exception:
        # 集合不存在或查询失败，返回空列表
        return []
