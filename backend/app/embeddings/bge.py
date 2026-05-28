from sentence_transformers import SentenceTransformer

_model = None
_model_name = None


def get_model(model_name: str = "BAAI/bge-small-zh-v1.5") -> SentenceTransformer:
    global _model, _model_name
    if _model is None or _model_name != model_name:
        _model = SentenceTransformer(model_name)
        _model_name = model_name
    return _model


def embed_texts(
    texts: list[str],
    model_name: str = "BAAI/bge-small-zh-v1.5",
) -> list[list[float]]:
    """批量文本向量化"""
    model = get_model(model_name)
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
