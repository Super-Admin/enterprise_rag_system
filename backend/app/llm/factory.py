from app.config import settings
from app.llm.base import BaseLLM
from app.llm.ollama import OllamaLLM
from app.llm.openai_llm import OpenAILLM


def get_llm() -> BaseLLM:
    """根据配置返回 LLM 实现"""
    if settings.llm_provider == "openai":
        return OpenAILLM(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    else:
        return OllamaLLM(model=settings.ollama_model)
