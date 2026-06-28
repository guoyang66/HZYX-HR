"""
OpenAI AI 适配器 - 基于 OpenAI 平台，使用 GPT-4o 模型
提供对话(Chat)、流式对话(Stream)、文本嵌入(Embed)能力
"""
import logging
from openai import OpenAI
from app.config import settings
from app.services.ai.adapter import AIModelAdapter

logger = logging.getLogger(__name__)


class OpenAIAdapter(AIModelAdapter):
    """OpenAI 适配器 - 直接调用 OpenAI API"""
    MODEL_ID = "openai"
    MODEL_NAME = "OpenAI"

    def __init__(self):
        self.enabled = settings.ai_openai_enabled and bool(settings.openai_api_key)
        if self.enabled:
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
            logger.info("OpenAIAdapter initialized (enabled: True)")

    def get_model_id(self) -> str:
        return self.MODEL_ID

    def get_model_name(self) -> str:
        return self.MODEL_NAME

    def is_enabled(self) -> bool:
        return self.enabled

    async def chat(self, messages: list[dict]) -> str:
        """调用 OpenAI 进行对话"""
        if not self.is_enabled():
            raise RuntimeError("OpenAI model is not enabled")
        try:
            response = self._client.chat.completions.create(
                model=settings.openai_chat_model,
                messages=messages,
            )
            content = response.choices[0].message.content or ""
            logger.debug("Chat completed, response length: %d", len(content))
            return content
        except Exception as e:
            logger.error("Chat error with OpenAI: %s", str(e))
            raise RuntimeError(f"Failed to chat with OpenAI model: {e}")

    async def stream(self, messages: list[dict]):
        """流式对话"""
        if not self.is_enabled():
            raise RuntimeError("OpenAI model is not enabled")
        try:
            response = self._client.chat.completions.create(
                model=settings.openai_chat_model,
                messages=messages,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error("Stream error with OpenAI: %s", str(e))
            raise RuntimeError(f"Failed to stream with OpenAI model: {e}")

    def embed(self, text: str) -> list[float]:
        """文本嵌入"""
        if not self.is_enabled():
            raise RuntimeError("OpenAI model is not enabled")
        try:
            response = self._client.embeddings.create(
                model=settings.openai_embedding_model,
                input=text,
            )
            embedding = response.data[0].embedding
            logger.debug("Embedding completed, dimension: %d", len(embedding))
            return embedding
        except Exception as e:
            logger.error("Embedding error with OpenAI: %s", str(e))
            raise RuntimeError(f"Failed to embed with OpenAI model: {e}")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量文本嵌入"""
        if not self.is_enabled():
            raise RuntimeError("OpenAI model is not enabled")
        try:
            response = self._client.embeddings.create(
                model=settings.openai_embedding_model,
                input=texts,
            )
            embeddings = [d.embedding for d in response.data]
            logger.debug("Batch embedding completed, count: %d", len(embeddings))
            return embeddings
        except Exception as e:
            logger.error("Batch embedding error with OpenAI: %s", str(e))
            raise RuntimeError(f"Failed to batch embed with OpenAI model: {e}")
