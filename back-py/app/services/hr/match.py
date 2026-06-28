"""
匹配调度服务 - 协调简历与岗位的匹配流程，调用混合匹配引擎并持久化结果
对应 Java 版本: MatchService.java
支持单次匹配、批量匹配（简历匹配所有岗位 / 岗位匹配所有简历）、历史查询
"""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resume import Resume
from app.models.position import Position
from app.models.match_record import MatchRecord
from app.schemas.match import MatchRequestDTO, MatchResultDTO
from app.api.exception_handlers import BusinessException

logger = logging.getLogger(__name__)


class MatchService:
    """匹配服务 - 简历与岗位的智能匹配调度中心"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def match(self, request: MatchRequestDTO, user_id: int) -> MatchResultDTO:
        """单次匹配：指定简历ID + 岗位ID，执行匹配并保存记录"""
        resume = await self._get_resume(request.resumeId)
        position = await self._get_position(request.positionId)

        # 调用混合匹配引擎
        result = await self._run_hybrid_match(resume, position, user_id)

        # 持久化匹配记录
        record = self._build_record(request.resumeId, request.positionId, result, user_id)
        self.db.add(record)
        await self.db.flush()

        return self._to_dto(record, resume.file_name or "", position.title)

    async def match_resume_to_positions(self, resume_id: int, user_id: int) -> list[MatchResultDTO]:
        """批量匹配：将指定简历与所有未删除的岗位逐一匹配"""
        resume = await self._get_resume(resume_id)
        result = await self.db.execute(select(Position).where(Position.deleted == False))
        positions = result.scalars().all()

        if not positions:
            return []

        from app.services.match.hybrid_match import HybridMatchService
        hybrid = HybridMatchService(self.db)
        results = []

        # 顺序处理（图谱匹配较快，避免会话冲突）
        for position in positions:
            try:
                match_result = await asyncio.wait_for(
                    hybrid.match(
                        resume.content or "",
                        resume.extracted_skills or [],
                        self._build_position_content(position),
                        position.skills or [],
                        user_id,
                    ),
                    timeout=15.0,  # 单岗位匹配超时15秒
                )
                record = self._build_record(resume_id, position.id, match_result, user_id)
                self.db.add(record)
                await self.db.flush()
                results.append(self._to_dto(record, resume.file_name or "", position.title))
            except Exception as e:
                logger.warning("Match failed for %s (id=%s): %s", position.title, position.id, str(e))

        return results

    async def match_position_to_resumes(self, position_id: int, user_id: int) -> list[MatchResultDTO]:
        """批量匹配：将指定岗位与所有简历逐一匹配"""
        position = await self._get_position(position_id)
        result = await self.db.execute(select(Resume))
        resumes = result.scalars().all()

        if not resumes:
            return []

        from app.services.match.hybrid_match import HybridMatchService
        hybrid = HybridMatchService(self.db)
        results = []

        for resume in resumes:
            try:
                match_result = await asyncio.wait_for(
                    hybrid.match(
                        resume.content or "",
                        resume.extracted_skills or [],
                        self._build_position_content(position),
                        position.skills or [],
                        user_id,
                    ),
                    timeout=15.0,
                )
                record = self._build_record(resume.id, position_id, match_result, user_id)
                self.db.add(record)
                await self.db.flush()
                results.append(self._to_dto(record, resume.file_name or "", position.title))
            except Exception as e:
                logger.warning("Match failed for resume %s (id=%s): %s", resume.file_name, resume.id, str(e))

        return results

    async def _run_hybrid_match(self, resume: Resume, position: Position, user_id: int):
        """执行混合匹配，带超时保护"""
        from app.services.match.hybrid_match import HybridMatchService
        hybrid = HybridMatchService(self.db)
        return await asyncio.wait_for(
            hybrid.match(
                resume.content or "",
                resume.extracted_skills or [],
                self._build_position_content(position),
                position.skills or [],
                user_id,
            ),
            timeout=15.0,  # 单次匹配超时15秒（AI不可用时快速降级）
        )

    async def get_match_record(self, match_id: int) -> MatchResultDTO:
        """根据ID获取匹配记录详情"""
        result = await self.db.execute(select(MatchRecord).where(MatchRecord.id == match_id))
        record = result.scalar_one_or_none()
        if not record:
            raise BusinessException("匹配记录不存在", 404)

        resume_name, position_title = await self._resolve_names(record.resume_id, record.position_id)
        return self._to_dto(record, resume_name, position_title)

    async def list_match_records(self, page: int, size: int) -> dict:
        """分页查询匹配记录列表"""
        count_query = select(func.count()).select_from(MatchRecord)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = select(MatchRecord).offset(page * size).limit(size).order_by(MatchRecord.created_at.desc())
        result = await self.db.execute(query)
        records = result.scalars().all()

        dto_list = []
        for r in records:
            resume_name, position_title = await self._resolve_names(r.resume_id, r.position_id)
            dto_list.append(self._to_dto(r, resume_name, position_title))

        return {
            "content": dto_list,
            "totalElements": total,
            "totalPages": max(1, (total + size - 1) // size),
            "number": page,
            "size": size,
        }

    async def get_resume_match_history(self, resume_id: int) -> list[MatchResultDTO]:
        """查询指定简历的所有匹配历史"""
        result = await self.db.execute(
            select(MatchRecord).where(MatchRecord.resume_id == resume_id).order_by(MatchRecord.created_at.desc())
        )
        records = result.scalars().all()
        return [self._to_dto(r, "", "") for r in records]

    async def get_position_match_history(self, position_id: int) -> list[MatchResultDTO]:
        """查询指定岗位的所有匹配历史"""
        result = await self.db.execute(
            select(MatchRecord).where(MatchRecord.position_id == position_id).order_by(MatchRecord.created_at.desc())
        )
        records = result.scalars().all()
        return [self._to_dto(r, "", "") for r in records]

    async def _resolve_names(self, resume_id: int, position_id: int) -> tuple[str, str]:
        """解析简历名称和岗位名称（用于DTO展示）"""
        resume_name = ""
        position_title = ""
        res = await self.db.execute(select(Resume).where(Resume.id == resume_id))
        if resume := res.scalar_one_or_none():
            resume_name = resume.file_name or ""
        pos = await self.db.execute(select(Position).where(Position.id == position_id))
        if position := pos.scalar_one_or_none():
            position_title = position.title
        return resume_name, position_title

    async def _get_resume(self, resume_id: int) -> Resume:
        """获取简历，不存在则抛404"""
        result = await self.db.execute(select(Resume).where(Resume.id == resume_id))
        resume = result.scalar_one_or_none()
        if not resume:
            raise BusinessException("简历不存在", 404)
        return resume

    async def _get_position(self, position_id: int) -> Position:
        """获取岗位（未删除），不存在则抛404"""
        result = await self.db.execute(select(Position).where(Position.id == position_id, Position.deleted == False))
        position = result.scalar_one_or_none()
        if not position:
            raise BusinessException("岗位不存在", 404)
        return position

    @staticmethod
    def _build_record(resume_id: int, position_id: int, match_result, user_id: int) -> MatchRecord:
        """构建匹配记录ORM对象"""
        return MatchRecord(
            resume_id=resume_id,
            position_id=position_id,
            final_score=match_result.final_score,
            rag_score=match_result.rag_score,
            graph_score=match_result.graph_score,
            llm_score=match_result.llm_score,
            matched_skills=match_result.matched_skills,
            missing_skills=match_result.missing_skills,
            llm_report=match_result.llm_report,
            matched_by=user_id,
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _build_position_content(position: Position) -> str:
        """构建岗位文本描述（用于LLM评估时拼接上下文）"""
        parts = [
            f"岗位: {position.title}",
            f"公司: {position.company or ''}",
            f"经验要求: {position.experience or ''}",
            f"学历要求: {position.education or ''}",
        ]
        if position.responsibilities:
            parts.append(f"岗位职责: {position.responsibilities}")
        if position.requirements:
            parts.append(f"任职要求: {position.requirements}")
        if position.skills:
            parts.append(f"技能要求: {', '.join(position.skills)}")
        return "\n".join(parts)

    @staticmethod
    def _to_dto(r: MatchRecord, resume_name: str, position_title: str) -> MatchResultDTO:
        """将数据库记录转为前端DTO"""
        return MatchResultDTO(
            id=r.id,
            resumeId=r.resume_id,
            positionId=r.position_id,
            resumeName=resume_name,
            positionTitle=position_title,
            finalScore=r.final_score,
            ragScore=r.rag_score,
            graphScore=r.graph_score,
            llmScore=r.llm_score,
            matchedSkills=r.matched_skills,
            missingSkills=r.missing_skills,
            extraSkills=[],
            llmReport=r.llm_report,
            matchGrade=_calculate_grade(r.final_score) if r.final_score is not None else "D",
            recommendLevel=_calculate_recommend_level(r.final_score) if r.final_score is not None else 1,
            scoreDetails={},
            createdAt=r.created_at,
        )


def _calculate_grade(score: float) -> str:
    """匹配等级转换"""
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def _calculate_recommend_level(score: float) -> int:
    """推荐星级转换"""
    if score >= 90:
        return 5
    if score >= 75:
        return 4
    if score >= 60:
        return 3
    if score >= 45:
        return 2
    return 1
