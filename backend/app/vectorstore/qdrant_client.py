import os

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.config import settings

# 排除本地地址的代理
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

_client = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, check_compatibility=False)
    return _client


def create_collection(kb_id: int, vector_size: int = 512):
    """为知识库创建向量集合"""
    client = get_client()
    collection_name = f"kb_{kb_id}"
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def upsert_chunks(
    kb_id: int,
    chunks: list[dict],
    vectors: list[list[float]],
):
    """写入向量 + payload"""
    client = get_client()
    collection_name = f"kb_{kb_id}"

    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(PointStruct(
            id=i,
            vector=vector,
            payload={
                "content": chunk["content"],
                "filename": chunk["metadata"].get("filename", ""),
                "page": chunk["metadata"].get("page", 1),
                "chunk_index": chunk["metadata"].get("chunk_index", 0),
            },
        ))

    client.upsert(collection_name=collection_name, points=points)


def search(
    kb_id: int,
    query_vector: list[float],
    top_k: int = 5,
) -> list[dict]:
    """向量相似度检索"""
    from qdrant_client.models import QueryRequest

    client = get_client()
    collection_name = f"kb_{kb_id}"

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
    )

    return [
        {
            "content": r.payload.get("content", ""),
            "filename": r.payload.get("filename", ""),
            "page": r.payload.get("page", 1),
            "score": r.score,
        }
        for r in results.points
    ]


def delete_document_chunks(kb_id: int, filename: str):
    """删除指定文档的所有向量"""
    client = get_client()
    collection_name = f"kb_{kb_id}"

    # 根据 filename 过滤删除
    client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="filename",
                    match=MatchValue(value=filename),
                )
            ]
        ),
    )
