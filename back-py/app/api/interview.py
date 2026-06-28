"""
面试题API路由 - 智能面试题生成、历史查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.interview import GenerateQuestionsRequest
from app.api.deps import get_current_user
from app.models.user import User
from app.services.interview.question_service import InterviewQuestionService

router = APIRouter()


@router.post("/generate")
async def generate_questions(
    request: GenerateQuestionsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """按请求参数生成面试题（支持指定技能/难度/类型/数量）"""
    service = InterviewQuestionService(db)
    result = await service.generate_questions(request, current_user.id)
    return ApiResponse.success(result.model_dump(), "面试题生成成功")


@router.post("/generate/position/{position_id}")
async def generate_by_position(
    position_id: int,
    difficulty: str | None = None,
    count: int = Query(5),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """快捷方法：按岗位生成面试题"""
    service = InterviewQuestionService(db)
    result = await service.generate_by_position(position_id, difficulty, count, current_user.id)
    return ApiResponse.success(result.model_dump(), "面试题生成成功")


@router.post("/generate/skills")
async def generate_by_skills(
    skills: list[str],
    difficulty: str | None = None,
    count: int = Query(5),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """快捷方法：按技能列表生成面试题"""
    service = InterviewQuestionService(db)
    result = await service.generate_by_skills(skills, difficulty, count, current_user.id)
    return ApiResponse.success(result.model_dump(), "面试题生成成功")


@router.get("/records/{record_id}")
async def get_record(record_id: int, db: AsyncSession = Depends(get_db)):
    """获取单条面试题记录"""
    service = InterviewQuestionService(db)
    result = await service.get_record(record_id)
    return ApiResponse.success(result.model_dump())


@router.get("/records")
async def list_records(
    page: int = Query(0),
    size: int = Query(10),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分页查询当前用户的面试题记录"""
    service = InterviewQuestionService(db)
    result = await service.list_records(current_user.id, page, size)
    return ApiResponse.success(result)


@router.delete("/records/{record_id}")
async def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除面试题记录"""
    service = InterviewQuestionService(db)
    await service.delete_record(record_id, current_user.id)
    return ApiResponse.success_message("面试记录删除成功")
