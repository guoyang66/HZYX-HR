"""
嵌入服务 - 文本转向量的统一接口，对上游屏蔽具体AI模型差异
"""
import logging
from app.services.ai.router import model_router

logger = logging.getLogger(__name__)


class EmbeddingService:
    """嵌入服务 - 将文本转换为向量表示（用于语义检索）"""

    def embed(self, text: str) -> list[float]:
        """将单段文本转为语义向量"""
        adapter = model_router.route()
        return adapter.embed(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量文本转向量"""
        adapter = model_router.route()
        return adapter.embed_batch(texts)
