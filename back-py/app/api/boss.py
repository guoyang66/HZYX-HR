"""
Boss Zhipin Integration API Routes - mirrors BossZhipinController.java
"""
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.boss import BossResumeRequest
from app.services.boss.boss_zhipin import BossZhipinService
from fastapi import Depends

router = APIRouter()


@router.post("/resume")
async def receive_resume(request: BossResumeRequest, db: AsyncSession = Depends(get_db)):
    service = BossZhipinService(db)
    result = await service.process_resume_and_match(request, 1)  # SYSTEM_HR_USER_ID = 1
    return ApiResponse.success(result.model_dump(), "简历已自动匹配并完成初审")
