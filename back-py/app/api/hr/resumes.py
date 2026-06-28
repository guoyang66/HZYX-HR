"""
简历管理API路由 - 上传、查询、删除简历
"""
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.services.hr.resume import ResumeService

router = APIRouter()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传简历（PDF/DOCX/TXT），自动解析文本并提取技能"""
    service = ResumeService(db)
    result = await service.upload_resume(file, current_user.id)
    return ApiResponse.success(result.model_dump(), "简历上传成功")


@router.get("/all")
async def get_all_resumes(db: AsyncSession = Depends(get_db)):
    """获取所有简历（用于匹配选择）"""
    service = ResumeService(db)
    resumes = await service.get_all_resumes()
    data = [r.model_dump() for r in resumes]
    return ApiResponse.success(data)


@router.get("")
async def list_resumes(
    page: int = Query(0),
    size: int = Query(10),
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """分页查询简历列表，支持按文件名搜索"""
    service = ResumeService(db)
    result = await service.list_resumes(page, size, keyword)
    return ApiResponse.success(result)


@router.get("/{resume_id}")
async def get_resume(resume_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个简历详情"""
    service = ResumeService(db)
    resume = await service.get_resume(resume_id)
    return ApiResponse.success(resume.model_dump())


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除简历及其文件和向量索引"""
    service = ResumeService(db)
    await service.delete_resume(resume_id, current_user.id)
    return ApiResponse.success_message("简历删除成功")
