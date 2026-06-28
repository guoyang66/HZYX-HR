
import logging
from app.services.rag.embedding import EmbeddingService
from app.services.vector.question_bank_store import QuestionBankVectorStore

logger = logging.getLogger(__name__)


class QuestionBankService:
    async def search_similar_questions(self, query: str, top_k: int = 5) -> list[dict]:
        """Search internal question bank for similar questions"""
        try:
            store = QuestionBankVectorStore()
            emb_service = EmbeddingService()
            query_embedding = emb_service.embed(query)
            results = await store.similarity_search(query_embedding, top_k=top_k)
            return results
        except Exception as e:
            logger.warning("Question bank search failed: %s", str(e))
            return []

    def format_results_as_context(self, results: list[dict]) -> str:
        """Format search results as prompt context"""
        if not results:
            return ""

        lines = ["\n\n参考题库（仅供参考，请勿直接复制）："]
        for i, r in enumerate(results, 1):
            content = r.get("content", "")
            lines.append(f"\n第{i}题：{content}")
        return "\n".join(lines)
