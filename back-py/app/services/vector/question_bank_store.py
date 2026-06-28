import json
import logging
from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, utility, connections
from app.config import settings
from app.services.vector.base import VectorStore

logger = logging.getLogger(__name__)


class QuestionBankVectorStore(VectorStore):
    def __init__(self):
        self._host = settings.milvus_host
        self._port = settings.milvus_port
        self._collection_name = settings.milvus_question_collection_name
        self._dim = settings.milvus_embedding_dimension
        self._init_connection()

    def _init_connection(self):
        try:
            connections.connect("default", host=self._host, port=str(self._port))
            self._ensure_collection()
        except Exception as e:
            logger.warning("QuestionBank VectorStore connection failed: %s", str(e))

    def _ensure_collection(self):
        if utility.has_collection(self._collection_name):
            return
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=128),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self._dim),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535),
        ]
        schema = CollectionSchema(fields, description="SmartHR Question Bank Vectors")
        collection = Collection(self._collection_name, schema)
        index_params = {
            "metric_type": settings.milvus_metric_type,
            "index_type": settings.milvus_index_type,
            "params": {"nlist": settings.milvus_nlist},
        }
        collection.create_index("embedding", index_params)
        collection.load()
        logger.info("Created QuestionBank collection: %s", self._collection_name)

    def get_store_id(self) -> str:
        return "question_bank"

    async def add_document(self, doc_id: str, content: str, embedding: list[float], metadata: dict = None):
        try:
            collection = Collection(self._collection_name)
            data = [[doc_id], [content], [embedding], [json.dumps(metadata or {})]]
            collection.insert(data)
            collection.flush()
        except Exception as e:
            logger.warning("Failed to add question: %s", str(e))

    async def add_documents(self, docs: list):
        try:
            collection = Collection(self._collection_name)
            ids, contents, embeddings, metas = [], [], [], []
            for doc_id, content, embedding, metadata in docs:
                ids.append(doc_id)
                contents.append(content)
                embeddings.append(embedding)
                metas.append(json.dumps(metadata or {}))
            collection.insert([ids, contents, embeddings, metas])
            collection.flush()
        except Exception as e:
            logger.warning("Failed to add questions: %s", str(e))

    async def delete_document(self, doc_id: str):
        try:
            collection = Collection(self._collection_name)
            collection.delete(f"id == '{doc_id}'")
        except Exception as e:
            logger.warning("Failed to delete question: %s", str(e))

    async def delete_documents(self, doc_ids: list[str]):
        try:
            collection = Collection(self._collection_name)
            ids_str = ", ".join(f"'{did}'" for did in doc_ids)
            collection.delete(f"id in [{ids_str}]")
        except Exception as e:
            logger.warning("Failed to delete questions: %s", str(e))

    async def similarity_search(self, query_embedding: list[float], top_k: int = 5, filter_expr: str = None) -> list[dict]:
        try:
            collection = Collection(self._collection_name)
            collection.load()
            search_params = {"metric_type": settings.milvus_metric_type, "params": {"nprobe": settings.milvus_nprobe}}
            results = collection.search([query_embedding], "embedding", search_params, limit=top_k, expr=filter_expr, output_fields=["id", "content", "metadata"])
            docs = []
            for hits in results:
                for hit in hits:
                    docs.append({"id": hit.id, "content": hit.entity.get("content", ""), "score": hit.distance, "metadata": json.loads(hit.entity.get("metadata", "{}"))})
            return docs
        except Exception as e:
            logger.warning("Failed to search questions: %s", str(e))
            return []

    async def get_document(self, doc_id: str) -> dict | None:
        try:
            collection = Collection(self._collection_name)
            collection.load()
            results = collection.query(expr=f"id == '{doc_id}'", output_fields=["id", "content", "metadata"])
            return results[0] if results else None
        except Exception:
            return None

    async def exists(self, doc_id: str) -> bool:
        return await self.get_document(doc_id) is not None

    async def count(self) -> int:
        try:
            collection = Collection(self._collection_name)
            collection.load()
            return collection.num_entities
        except Exception:
            return 0
