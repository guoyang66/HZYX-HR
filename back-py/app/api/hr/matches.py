"""
匹配分析API路由 - 简历与岗位的智能匹配及历史查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.match import MatchRequestDTO
from app.api.deps import get_current_user
from app.models.user import User
from app.services.hr.match import MatchService

router = APIRouter()


@router.post("")
async def match(
    request: MatchRequestDTO,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """单次匹配：指定简历与岗位进行人岗匹配分析"""
    service = MatchService(db)
    result = await service.match(request, current_user.id)
    return ApiResponse.success(result.model_dump(), "匹配完成")


@router.post("/resume/{resume_id}/positions")
async def match_resume_to_positions(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """批量匹配：将指定简历与所有岗位逐一匹配"""
    service = MatchService(db)
    results = await service.match_resume_to_positions(resume_id, current_user.id)
    data = [r.model_dump() for r in results]
    return ApiResponse.success(data, "匹配完成")


@router.post("/position/{position_id}/resumes")
async def match_position_to_resumes(
    position_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """批量匹配：将指定岗位与所有简历逐一匹配"""
    service = MatchService(db)
    results = await service.match_position_to_resumes(position_id, current_user.id)
    data = [r.model_dump() for r in results]
    return ApiResponse.success(data, "匹配完成")


@router.get("/resume/{resume_id}/history")
async def get_resume_match_history(resume_id: int, db: AsyncSession = Depends(get_db)):
    """查询指定简历的历史匹配记录"""
    service = MatchService(db)
    results = await service.get_resume_match_history(resume_id)
    data = [r.model_dump() for r in results]
    return ApiResponse.success(data)


@router.get("/position/{position_id}/history")
async def get_position_match_history(position_id: int, db: AsyncSession = Depends(get_db)):
    """查询指定岗位的历史匹配记录"""
    service = MatchService(db)
    results = await service.get_position_match_history(position_id)
    data = [r.model_dump() for r in results]
    return ApiResponse.success(data)


@router.get("")
async def list_match_records(
    page: int = Query(0),
    size: int = Query(10),
    db: AsyncSession = Depends(get_db),
):
    """分页查询所有匹配记录"""
    service = MatchService(db)
    result = await service.list_match_records(page, size)
    return ApiResponse.success(result)


@router.get("/{match_id}")
async def get_match_record(match_id: int, db: AsyncSession = Depends(get_db)):
    """获取单条匹配记录详情"""
    service = MatchService(db)
    result = await service.get_match_record(match_id)
    return ApiResponse.success(result.model_dump())
