from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.models import user, knowledge_base, document, chunk, chat
from app.api.auth import router as auth_router
from app.api.knowledge_base import router as kb_router
from app.api.document import router as doc_router
from app.api.chat import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="企业知识库 RAG 系统", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(kb_router)
app.include_router(doc_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/health")
def api_health():
    return {"status": "ok", "version": "0.1.0", "env": settings.app_env}
