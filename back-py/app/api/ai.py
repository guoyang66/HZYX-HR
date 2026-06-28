"""
AI模型管理API - 查看可用模型、切换模型
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.ai import SwitchModelRequest
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/models")
async def get_models(current_user: User = Depends(get_current_user)):
    """获取所有可用的AI模型列表（供前端下拉选择）"""
    from app.services.ai.registry import model_registry
    from app.services.ai.router import model_router
    models = model_router.get_available_models(current_user.id)
    return ApiResponse.success(models)


@router.get("/current")
async def get_current_model(current_user: User = Depends(get_current_user)):
    """获取当前使用的AI模型信息"""
    from app.services.ai.router import model_router
    info = model_router.get_current_model_info(current_user.id)
    return ApiResponse.success(info)


@router.post("/switch")
async def switch_model(
    request: SwitchModelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """切换当前用户的AI模型偏好并保存到数据库"""
    from app.services.ai.registry import model_registry
    from app.api.exception_handlers import BusinessException

    if not model_registry.is_enabled(request.modelId):
        raise BusinessException("指定的模型不可用或不存在: " + request.modelId)

    current_user.preferred_model = request.modelId
    await db.flush()

    result = {
        "success": True,
        "modelId": request.modelId,
        "message": "模型切换成功",
    }
    return ApiResponse.success(result)
