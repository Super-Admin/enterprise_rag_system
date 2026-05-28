import httpx

from app.config import settings
from app.llm.base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
        self.base_url = settings.ollama_base_url

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["response"]
