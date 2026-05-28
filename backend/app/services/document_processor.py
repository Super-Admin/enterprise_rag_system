from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chunk import Chunk
from app.services.document_parser import parse_document
from app.services.chunker import chunk_pages
from app.embeddings.bge import embed_texts
from app.vectorstore.qdrant_client import create_collection, upsert_chunks


def process_document(db: Session, document_id: int):
    """处理文档：解析 → 切片 → 向量化 → 入库"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return

    try:
        # 1. 解析
        doc.status = "parsing"
        db.commit()
        pages = parse_document(doc.file_path)

        # 2. 切片
        doc.status = "chunking"
        db.commit()
        chunks = chunk_pages(pages)

        # 3. 向量化
        doc.status = "vectorizing"
        db.commit()
        texts = [c["content"] for c in chunks]
        vectors = embed_texts(texts)

        # 4. 写入 Qdrant
        try:
            create_collection(doc.kb_id, vector_size=len(vectors[0]))
        except Exception:
            pass  # 集合可能已存在
        upsert_chunks(doc.kb_id, chunks, vectors)

        # 5. 写入 PostgreSQL chunks 表
        for i, chunk in enumerate(chunks):
            db_chunk = Chunk(
                document_id=doc.id,
                content=chunk["content"],
                chunk_index=i,
                chunk_metadata=chunk["metadata"],
            )
            db.add(db_chunk)

        doc.status = "done"
        db.commit()

    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)[:500]
        db.commit()
        raise e
