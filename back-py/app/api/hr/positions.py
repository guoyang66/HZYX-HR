"""
岗位管理API路由 - 岗位CRUD操作
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.position import PositionCreateRequest, PositionUpdateRequest
from app.api.deps import get_current_user
from app.models.user import User
from app.services.hr.position import PositionService

router = APIRouter()


@router.post("")
async def create_position(
    request: PositionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新岗位（包含技能标签）"""
    service = PositionService(db)
    position = await service.create_position(request, current_user.id)
    return ApiResponse.success(position.model_dump(), "岗位创建成功")


@router.get("/all")
async def get_all_positions(db: AsyncSession = Depends(get_db)):
    """获取所有未删除岗位（用于下拉选择）"""
    service = PositionService(db)
    positions = await service.get_all_positions()
    data = [p.model_dump() for p in positions]
    return ApiResponse.success(data)


@router.get("")
async def list_positions(
    page: int = Query(0),
    size: int = Query(10),
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """分页查询岗位，支持按标题/公司搜索"""
    service = PositionService(db)
    result = await service.list_positions(page, size, keyword)
    return ApiResponse.success(result)


@router.get("/{position_id}")
async def get_position(position_id: int, db: AsyncSession = Depends(get_db)):
    """获取岗位详情"""
    service = PositionService(db)
    position = await service.get_position(position_id)
    return ApiResponse.success(position.model_dump())


@router.put("/{position_id}")
async def update_position(
    position_id: int,
    request: PositionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新岗位信息"""
    service = PositionService(db)
    position = await service.update_position(position_id, request, current_user.id)
    return ApiResponse.success(position.model_dump(), "岗位更新成功")


@router.delete("/{position_id}")
async def delete_position(
    position_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """软删除岗位"""
    service = PositionService(db)
    await service.delete_position(position_id, current_user.id)
    return ApiResponse.success_message("岗位删除成功")
