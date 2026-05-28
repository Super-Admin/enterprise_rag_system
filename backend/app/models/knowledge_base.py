from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), default="")
    embedding_model = Column(String(50), default="bge-small")
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="knowledge_base")
