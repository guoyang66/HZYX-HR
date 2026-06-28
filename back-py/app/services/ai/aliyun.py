"""
阿里云百炼 AI 适配器 - 基于 DashScope 平台，使用 qwen-plus 模型
提供对话(Chat)、流式对话(Stream)、文本嵌入(Embed)能力
"""
import logging
from dashscope import Generation
from dashscope.api_entities.dashscope_response import GenerationResponse
from http import HTTPStatus
from openai import OpenAI
from app.config import settings
from app.services.ai.adapter import AIModelAdapter

logger = logging.getLogger(__name__)


class AliyunAdapter(AIModelAdapter):
    """阿里云百炼 AI 适配器 - 通过 OpenAI 兼容接口访问 DashScope"""
    MODEL_ID = "aliyun"
    MODEL_NAME = "阿里云百炼"

    def __init__(self):
        self.enabled = settings.ai_aliyun_enabled and bool(settings.dashscope_api_key)
        if self.enabled:
            self._client = OpenAI(
                api_key=settings.dashscope_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            logger.info("AliyunAdapter initialized (enabled: True)")

    def get_model_id(self) -> str:
        return self.MODEL_ID

    def get_model_name(self) -> str:
        return self.MODEL_NAME

    def is_enabled(self) -> bool:
        return self.enabled

    async def chat(self, messages: list[dict]) -> str:
        """调用阿里云百炼进行对话，返回完整回复文本"""
        if not self.is_enabled():
            raise RuntimeError("Aliyun model is not enabled")
        try:
            response = self._client.chat.completions.create(
                model=settings.dashscope_chat_model,
                messages=messages,
                temperature=settings.dashscope_temperature,
            )
            content = response.choices[0].message.content or ""
            logger.debug("Chat completed, response length: %d", len(content))
            return content
        except Exception as e:
            logger.error("Chat error with Aliyun: %s", str(e))
            raise RuntimeError(f"Failed to chat with Aliyun model: {e}")

    async def stream(self, messages: list[dict]):
        """流式对话：逐步返回AI回复的文本片段"""
        if not self.is_enabled():
            raise RuntimeError("Aliyun model is not enabled")
        try:
            response = self._client.chat.completions.create(
                model=settings.dashscope_chat_model,
                messages=messages,
                temperature=settings.dashscope_temperature,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error("Stream error with Aliyun: %s", str(e))
            raise RuntimeError(f"Failed to stream with Aliyun model: {e}")

    def embed(self, text: str) -> list[float]:
        """文本嵌入：将文本转为向量（用于语义检索）"""
        if not self.is_enabled():
            raise RuntimeError("Aliyun model is not enabled")
        try:
            response = self._client.embeddings.create(
                model=settings.dashscope_embedding_model,
                input=text,
            )
            embedding = response.data[0].embedding
            logger.debug("Embedding completed, dimension: %d", len(embedding))
            return embedding
        except Exception as e:
            logger.error("Embedding error with Aliyun: %s", str(e))
            raise RuntimeError(f"Failed to embed with Aliyun model: {e}")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量文本嵌入"""
        if not self.is_enabled():
            raise RuntimeError("Aliyun model is not enabled")
        try:
            response = self._client.embeddings.create(
                model=settings.dashscope_embedding_model,
                input=texts,
            )
            embeddings = [d.embedding for d in response.data]
            logger.debug("Batch embedding completed, count: %d", len(embeddings))
            return embeddings
        except Exception as e:
            logger.error("Batch embedding error with Aliyun: %s", str(e))
            raise RuntimeError(f"Failed to batch embed with Aliyun model: {e}")
