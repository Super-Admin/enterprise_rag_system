from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.models.chat import Chat, Message
from app.api.deps import get_current_user
from app.rag.pipeline import run_rag

router = APIRouter(prefix="/api/chat", tags=["聊天"])


class ChatRequest(BaseModel):
    kb_id: int
    message: str
    chat_id: int | None = None


class ChatResponse(BaseModel):
    chat_id: int
    answer: str
    sources: list[dict]


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == req.kb_id,
        KnowledgeBase.user_id == current_user.id,
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 创建或复用会话
    if req.chat_id:
        chat_obj = db.query(Chat).filter(
            Chat.id == req.chat_id,
            Chat.user_id == current_user.id,
        ).first()
        if not chat_obj:
            raise HTTPException(status_code=404, detail="会话不存在")
    else:
        chat_obj = Chat(
            user_id=current_user.id,
            kb_id=req.kb_id,
            title=req.message[:50],
        )
        db.add(chat_obj)
        db.commit()
        db.refresh(chat_obj)

    # 保存用户消息
    user_msg = Message(chat_id=chat_obj.id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()

    # RAG 问答
    result = await run_rag(req.kb_id, req.message)

    # 保存助手消息
    assistant_msg = Message(
        chat_id=chat_obj.id,
        role="assistant",
        content=result["answer"],
        sources=result["sources"],
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        chat_id=chat_obj.id,
        answer=result["answer"],
        sources=result["sources"],
    )


@router.get("/history")
def get_history(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat_obj = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
    ).first()
    if not chat_obj:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sources": m.sources,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]
