"""
Milvus 向量存储实现 - 基于 Milvus 的文档向量索引和语义检索
支持简历文本和面试题的向量化存储与相似度搜索
"""
import json
import logging
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from app.config import settings
from app.services.vector.base import VectorStore, VectorDocument

logger = logging.getLogger(__name__)


class MilvusVectorStore(VectorStore):
    """Milvus向量存储 - 文档索引和语义搜索的向量数据库实现"""

    def __init__(self):
        self._host = settings.milvus_host
        self._port = settings.milvus_port
        self._collection_name = settings.milvus_collection_name
        self._dim = settings.milvus_embedding_dimension
        self._init_connection()

    def _init_connection(self):
        """初始化Milvus连接并确保集合存在"""
        try:
            connections.connect("default", host=self._host, port=str(self._port))
            self._ensure_collection()
            logger.info("MilvusVectorStore connected to %s:%s", self._host, self._port)
        except Exception as e:
            logger.warning("Milvus connection failed: %s. Vector features disabled.", str(e))

    def _ensure_collection(self):
        """确保向量集合存在，不存在则自动创建并建立索引"""
        if utility.has_collection(self._collection_name):
            return
        # 定义集合Schema：id(主键)、content(原文)、embedding(向量)、metadata(元数据)
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=128),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self._dim),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535),
        ]
        schema = CollectionSchema(fields, description="SmartHR Resume Vectors")
        collection = Collection(self._collection_name, schema)
        # 创建IVF_FLAT索引（余弦相似度）
        index_params = {
            "metric_type": settings.milvus_metric_type,
            "index_type": settings.milvus_index_type,
            "params": {"nlist": settings.milvus_nlist},
        }
        collection.create_index("embedding", index_params)
        collection.load()
        logger.info("Created Milvus collection: %s", self._collection_name)

    def get_store_id(self) -> str:
        return "milvus"

    async def add_document(self, doc_id: str, content: str, embedding: list[float], metadata: dict = None):
        """添加单个文档向量"""
        try:
            collection = Collection(self._collection_name)
            data = [[doc_id], [content], [embedding], [json.dumps(metadata or {})]]
            collection.insert(data)
            collection.flush()
            logger.debug("Added document to Milvus: %s", doc_id)
        except Exception as e:
            logger.warning("Failed to add document to Milvus: %s", str(e))

    async def add_documents(self, docs: list[tuple]):
        """批量添加文档向量"""
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
            logger.warning("Failed to add documents to Milvus: %s", str(e))

    async def delete_document(self, doc_id: str):
        """删除指定文档"""
        try:
            collection = Collection(self._collection_name)
            collection.delete(f"id == '{doc_id}'")
            logger.debug("Deleted document from Milvus: %s", doc_id)
        except Exception as e:
            logger.warning("Failed to delete document from Milvus: %s", str(e))

    async def delete_documents(self, doc_ids: list[str]):
        """批量删除文档"""
        try:
            collection = Collection(self._collection_name)
            ids_str = ", ".join(f"'{did}'" for did in doc_ids)
            collection.delete(f"id in [{ids_str}]")
        except Exception as e:
            logger.warning("Failed to delete documents from Milvus: %s", str(e))

    async def similarity_search(self, query_embedding: list[float], top_k: int = 5, filter_expr: str = None) -> list[dict]:
        """向量相似度检索：返回与查询向量最相似的前K个文档"""
        try:
            collection = Collection(self._collection_name)
            collection.load()
            search_params = {
                "metric_type": settings.milvus_metric_type,
                "params": {"nprobe": settings.milvus_nprobe},
            }
            results = collection.search(
                [query_embedding],
                "embedding",
                search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=["id", "content", "metadata"],
            )
            docs = []
            for hits in results:
                for hit in hits:
                    docs.append({
                        "id": hit.id,
                        "content": hit.entity.get("content", ""),
                        "score": hit.distance,  # 余弦相似度得分
                        "metadata": json.loads(hit.entity.get("metadata", "{}")),
                    })
            return docs
        except Exception as e:
            logger.warning("Failed to search Milvus: %s", str(e))
            return []

    async def get_document(self, doc_id: str) -> dict | None:
        """按ID获取文档"""
        try:
            collection = Collection(self._collection_name)
            collection.load()
            results = collection.query(expr=f"id == '{doc_id}'", output_fields=["id", "content", "metadata"])
            return results[0] if results else None
        except Exception as e:
            logger.warning("Failed to get document from Milvus: %s", str(e))
            return None

    async def exists(self, doc_id: str) -> bool:
        """检查文档是否存在"""
        return await self.get_document(doc_id) is not None

    async def count(self) -> int:
        """获取文档总数"""
        try:
            collection = Collection(self._collection_name)
            collection.load()
            return collection.num_entities
        except Exception:
            return 0
