import os

import fitz  # pymupdf
from docx import Document as DocxDocument


def parse_document(file_path: str) -> list[dict]:
    """解析文档，返回 [{content, page, source}]"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    elif ext in (".txt", ".md"):
        return parse_text(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")


def parse_pdf(file_path: str) -> list[dict]:
    doc = fitz.open(file_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append({
                "content": text.strip(),
                "page": i + 1,
                "source": os.path.basename(file_path),
            })
    doc.close()
    return pages


def parse_docx(file_path: str) -> list[dict]:
    doc = DocxDocument(file_path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [{
        "content": full_text,
        "page": 1,
        "source": os.path.basename(file_path),
    }]


def parse_text(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return [{
        "content": content.strip(),
        "page": 1,
        "source": os.path.basename(file_path),
    }]
