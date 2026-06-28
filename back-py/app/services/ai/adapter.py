"""
AI模型适配器抽象基类 - 定义统一的AI模型接口（适配器模式）
所有AI模型实现（阿里云百炼、OpenAI等）都需继承此类并实现所有抽象方法
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator


class AIModelAdapter(ABC):
    """AI模型适配器基类 - 屏蔽不同AI平台的差异，提供统一接口"""

    @abstractmethod
    def get_model_id(self) -> str:
        """获取模型唯一标识（如 aliyun、openai）"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型显示名称（如 阿里云百炼、OpenAI）"""
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """检查模型是否已启用（配置了API Key等必要条件）"""
        pass

    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        """对话接口：发送消息列表，获取AI回复"""
        pass

    @abstractmethod
    async def stream(self, messages: list[dict]):
        """流式对话接口：逐步返回AI回复片段"""
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """文本嵌入：将文本转为向量（用于语义检索）"""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量文本嵌入"""
        pass
