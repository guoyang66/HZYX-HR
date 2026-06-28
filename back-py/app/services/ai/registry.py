"""
AI模型注册中心 - 管理所有已注册的AI模型适配器实例（注册表模式 + 单例）
"""
import logging
from app.services.ai.adapter import AIModelAdapter

logger = logging.getLogger(__name__)


class ModelRegistry:
    """模型注册中心 - 维护 model_id -> adapter 的映射，支持热注册、查询、启用检查"""

    def __init__(self):
        self._adapters: dict[str, AIModelAdapter] = {}

    def register(self, adapter: AIModelAdapter):
        """注册AI模型适配器"""
        self._adapters[adapter.get_model_id()] = adapter
        logger.info("Registered AI model adapter: %s (%s), enabled: %s",
                     adapter.get_model_name(), adapter.get_model_id(), adapter.is_enabled())

    def get(self, model_id: str) -> AIModelAdapter | None:
        """根据模型ID获取适配器"""
        return self._adapters.get(model_id)

    def get_all(self) -> list[AIModelAdapter]:
        """获取所有适配器（含未启用的）"""
        return list(self._adapters.values())

    def get_enabled(self) -> list[AIModelAdapter]:
        """获取所有已启用的适配器"""
        return [a for a in self._adapters.values() if a.is_enabled()]

    def is_enabled(self, model_id: str) -> bool:
        """检查指定模型是否已启用"""
        adapter = self._adapters.get(model_id)
        return adapter is not None and adapter.is_enabled()

    def get_all_model_ids(self) -> list[str]:
        """获取所有模型ID列表"""
        return list(self._adapters.keys())

    def get_enabled_model_ids(self) -> list[str]:
        """获取所有已启用模型的ID列表"""
        return [k for k, v in self._adapters.items() if v.is_enabled()]


# 全局注册中心单例
model_registry = ModelRegistry()
