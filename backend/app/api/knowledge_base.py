from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.api.deps import get_current_user
from app.api.kb_schemas import KBCreate, KBResponse

router = APIRouter(prefix="/api/kb", tags=["知识库"])


@router.post("/create", response_model=KBResponse, status_code=status.HTTP_201_CREATED)
def create_kb(
    data: KBCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = KnowledgeBase(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        embedding_model=data.embedding_model,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


@router.get("/list", response_model=list[KBResponse])
def list_kbs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(KnowledgeBase).filter(KnowledgeBase.user_id == current_user.id).all()


@router.get("/{kb_id}", response_model=KBResponse)
def get_kb(
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
    return kb


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kb(
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
    db.delete(kb)
    db.commit()
