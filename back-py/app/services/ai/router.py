"""
AI模型路由器 - 根据用户偏好和可用性智能分配最优AI模型（路由模式 + 单例）
"""
import logging
from app.config import settings
from app.services.ai.adapter import AIModelAdapter
from app.services.ai.registry import model_registry

logger = logging.getLogger(__name__)


class ModelRouter:
    """模型路由器 - 决策当前请求使用哪个AI模型"""

    def route(self, user_id: int | None = None) -> AIModelAdapter:
        """路由决策：先用用户偏好模型，不可用时按优先级降级（aliyun -> openai）"""
        if user_id is not None:
            # 未来可扩展：根据数据库中的用户preferred_model字段来路由
            pass
        return self._get_default_adapter()

    def get_current_model_info(self, user_id: int | None = None) -> dict:
        """获取当前使用的模型信息（用于前端展示）"""
        adapter = self.route(user_id)
        return {
            "modelId": adapter.get_model_id(),
            "modelName": adapter.get_model_name(),
            "enabled": adapter.is_enabled(),
        }

    def get_available_models(self, user_id: int | None = None) -> list[dict]:
        """获取所有可用模型列表（供前端切换模型用）"""
        current_id = self.get_current_model_info(user_id)["modelId"]
        return [
            {
                "modelId": a.get_model_id(),
                "modelName": a.get_model_name(),
                "enabled": a.is_enabled(),
                "current": a.get_model_id() == current_id,
            }
            for a in sorted(model_registry.get_enabled(), key=lambda x: x.get_model_id())
        ]

    def _get_default_adapter(self) -> AIModelAdapter:
        """获取默认适配器：配置默认 -> aliyun -> openai 的降级顺序"""
        # 优先使用配置的默认模型
        default = settings.ai_default_model
        if default:
            adapter = model_registry.get(default)
            if adapter and adapter.is_enabled():
                return adapter

        # 降级顺序：阿里云 -> OpenAI
        for mid in ["aliyun", "openai"]:
            adapter = model_registry.get(mid)
            if adapter and adapter.is_enabled():
                return adapter

        raise RuntimeError("No available AI model. Please check DashScope/OpenAI configuration.")


# 全局路由器单例
model_router = ModelRouter()
