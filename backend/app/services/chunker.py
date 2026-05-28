def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """按字符数切片文本"""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """切片文档页面，返回 [{content, metadata}]"""
    result = []
    for page in pages:
        chunks = chunk_text(page["content"], chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            result.append({
                "content": chunk,
                "metadata": {
                    "filename": page.get("source", ""),
                    "page": page.get("page", 1),
                    "chunk_index": i,
                    "source": page.get("source", ""),
                },
            })
    return result
