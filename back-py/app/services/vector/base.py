"""
向量存储抽象基类 - 定义统一的向量数据库操作接口（策略模式）
所有向量存储实现（如 Milvus）都需继承此类
"""
from abc import ABC, abstractmethod


class VectorStore(ABC):
    """向量存储基类 - 提供文档的语义索引和相似度检索能力"""

    @abstractmethod
    def get_store_id(self) -> str:
        """获取存储标识"""
        pass

    @abstractmethod
    async def add_document(self, doc_id: str, content: str, embedding: list[float], metadata: dict = None):
        """添加单个文档到向量库"""
        pass

    @abstractmethod
    async def add_documents(self, docs: list[tuple[str, str, list[float], dict]]):
        """批量添加文档"""
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str):
        """删除指定文档"""
        pass

    @abstractmethod
    async def delete_documents(self, doc_ids: list[str]):
        """批量删除文档"""
        pass

    @abstractmethod
    async def similarity_search(self, query_embedding: list[float], top_k: int = 5, filter_expr: str = None) -> list[dict]:
        """相似度检索：返回与查询向量最相似的前K个文档"""
        pass

    @abstractmethod
    async def get_document(self, doc_id: str) -> dict | None:
        """获取指定文档"""
        pass

    @abstractmethod
    async def exists(self, doc_id: str) -> bool:
        """检查文档是否存在"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """获取文档总数"""
        pass


class VectorDocument:
    """向量文档实体"""
    def __init__(self, id: str, content: str, embedding: list[float] = None, metadata: dict = None, score: float = 0.0):
        self.id = id
        self.content = content
        self.embedding = embedding or []
        self.metadata = metadata or {}
        self.score = score  # 相似度得分
