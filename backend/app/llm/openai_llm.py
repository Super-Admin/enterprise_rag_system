from openai import AsyncOpenAI

from app.llm.base import BaseLLM


class OpenAILLM(BaseLLM):
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str = "",
        base_url: str = "https://api.openai.com/v1",
    ):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
