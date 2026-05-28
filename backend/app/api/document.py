import os
import threading

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document
from app.api.deps import get_current_user
from app.api.kb_schemas import DocumentResponse
from app.services.document_processor import process_document

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

router = APIRouter(prefix="/api/document", tags=["文档"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    kb_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id,
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制(50MB)")

    kb_dir = os.path.join(UPLOAD_DIR, str(kb_id))
    os.makedirs(kb_dir, exist_ok=True)
    file_path = os.path.join(kb_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        kb_id=kb_id,
        filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        status="uploading",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 异步处理文档
    def process_in_background(doc_id: int):
        bg_db = SessionLocal()
        try:
            process_document(bg_db, doc_id)
        except Exception as e:
            doc = bg_db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.status = "failed"
                doc.error_message = str(e)[:500]
                bg_db.commit()
        finally:
            bg_db.close()

    thread = threading.Thread(target=process_in_background, args=(doc.id,))
    thread.daemon = True
    thread.start()

    return doc


@router.get("/list", response_model=list[DocumentResponse])
def list_documents(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id,
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return db.query(Document).filter(Document.kb_id == kb_id).all()


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).join(KnowledgeBase).filter(
        Document.id == doc_id,
        KnowledgeBase.user_id == current_user.id,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 删除 Qdrant 中的向量
    try:
        from app.vectorstore.qdrant_client import delete_document_chunks
        delete_document_chunks(doc.kb_id, doc.filename)
    except Exception:
        pass  # 集合可能不存在

    # 删除 chunks 记录
    from app.models.chunk import Chunk
    db.query(Chunk).filter(Chunk.document_id == doc.id).delete()

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # 删除文档记录
    db.delete(doc)
    db.commit()
