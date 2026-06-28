
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resume import Resume
from app.models.position import Position
from app.models.match_record import MatchRecord
from app.schemas.boss import BossResumeRequest, BossMatchResponse, PositionMatchItem
from app.api.exception_handlers import BusinessException
from app.services.document.skill_extractor import SkillExtractor
from app.services.match.hybrid_match import HybridMatchService
from app.services.ai.router import model_router

logger = logging.getLogger(__name__)

SYSTEM_HR_USER_ID = 1
SCREENING_THRESHOLD = 60.0


class BossZhipinService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_resume_and_match(self, request: BossResumeRequest, user_id: int) -> BossMatchResponse:
        logger.info("Processing Boss resume: sourceId=%s, candidate=%s", request.sourceResumeId, request.candidateName)

        # 1. Extract skills
        extractor = SkillExtractor()
        extracted_skills = await extractor.extract_skills(request.resumeContent, user_id, self.db)
        normalized_skills = await extractor.normalize_skills(extracted_skills)

        # 2. Save resume
        display_name = (request.candidateName + "_" if request.candidateName else "") + "boss_" + (request.sourceResumeId or "unknown")
        resume = Resume(
            user_id=user_id,
            file_name=display_name,
            content=request.resumeContent,
            extracted_skills=normalized_skills,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(resume)
        await self.db.flush()

        # 3. Get all positions
        result = await self.db.execute(select(Position).where(Position.deleted == False))
        all_positions = result.scalars().all()
        if not all_positions:
            raise BusinessException("系统中没有可匹配的岗位，请先在HR管理中添加岗位")

        # 4. Prioritize positions by desired position
        matched_positions = self._prioritize_positions(all_positions, request.desiredPosition)

        # 5. Match all positions in parallel
        hybrid = HybridMatchService(self.db)
        match_items = []

        async def match_one(position):
            try:
                pos_content = self._build_position_content(position)
                result = await hybrid.match(
                    resume.content or "",
                    resume.extracted_skills or [],
                    pos_content,
                    position.skills or [],
                    user_id,
                )
                record = MatchRecord(
                    resume_id=resume.id,
                    position_id=position.id,
                    final_score=result.final_score,
                    rag_score=result.rag_score,
                    graph_score=result.graph_score,
                    llm_score=result.llm_score,
                    matched_skills=result.matched_skills,
                    missing_skills=result.missing_skills,
                    llm_report=result.llm_report,
                    matched_by=user_id,
                    created_at=datetime.now(timezone.utc),
                )
                self.db.add(record)
                await self.db.flush()
                return PositionMatchItem(
                    positionId=position.id,
                    positionTitle=position.title,
                    finalScore=result.final_score,
                    graphScore=result.graph_score,
                    llmScore=result.llm_score,
                    matchGrade=self._calculate_grade(result.final_score),
                    matchedSkills=result.matched_skills,
                    missingSkills=result.missing_skills,
                    llmReport=result.llm_report,
                    passedScreening=result.final_score >= SCREENING_THRESHOLD,
                    recommendLevel=self._calculate_recommend_level(result.final_score),
                )
            except Exception as e:
                logger.warning("Boss匹配岗位 [%s] 失败: %s", position.title, str(e))
                return None

        tasks = [match_one(p) for p in matched_positions]
        results = await asyncio.gather(*tasks)
        match_items = [r for r in results if r is not None]

        # 6. Sort by score descending
        match_items.sort(key=lambda x: x.finalScore or 0, reverse=True)

        # 7. Generate screening report
        screening_report = await self._generate_screening_report(request, match_items, user_id)
        recommend = self._evaluate_recommendation(match_items)

        return BossMatchResponse(
            sourceResumeId=request.sourceResumeId,
            candidateName=request.candidateName,
            matchedPositionCount=len(match_items),
            positionMatches=match_items,
            overallVerdict="推荐进入面试" if recommend else "暂不推荐",
            overallScore=match_items[0].finalScore if match_items else 0,
            llmScreeningReport=screening_report,
            recommendInterview=recommend,
            processedAt=datetime.now(timezone.utc),
        )

    def _prioritize_positions(self, all_positions: list[Position], desired: str | None) -> list[Position]:
        if not desired:
            return list(all_positions)
        result = []
        others = []
        for p in all_positions:
            if p.title and desired in p.title:
                result.append(p)
            else:
                others.append(p)
        result.extend(others)
        return result

    async def _generate_screening_report(self, request: BossResumeRequest, matches: list[PositionMatchItem], user_id: int) -> str:
        try:
            match_summary = ""
            for i, item in enumerate(matches[:5]):
                match_summary += f"- {item.positionTitle}（岗位ID: {item.positionId}）: 综合分数 {item.finalScore:.1f}，等级 {item.matchGrade}，技能匹配: {', '.join(item.matchedSkills or [])}\n"

            prompt = f"""你是HR初筛助手。请根据以下候选人简历和岗位匹配结果，给出综合初审意见（100字以内）。

候选人信息：
- 姓名: {request.candidateName or '未知'}
- 意向岗位: {request.desiredPosition or '未填写'}
- 工作年限: {request.workYears or '未知'}
- 学历: {request.education or '未知'}

匹配结果（前{min(len(matches), 5)}个岗位）：
{match_summary}

请判断：该候选人是否推荐进入面试？给出理由。"""

            adapter = model_router.route(user_id)
            return await adapter.chat([{"role": "user", "content": prompt}])
        except Exception as e:
            logger.warning("LLM 综合初审报告生成失败: %s", str(e))
            return self._build_fallback_report(matches)

    def _build_fallback_report(self, matches: list[PositionMatchItem]) -> str:
        if not matches:
            return "无匹配岗位，无法评估。"
        best = matches[0]
        passed = sum(1 for m in matches if m.passedScreening)
        return f"【自动评估】共匹配{len(matches)}个岗位，最佳匹配: {best.positionTitle}（分数{best.finalScore:.1f}），通过初审阈值({SCREENING_THRESHOLD:.0f}分)的岗位: {passed}个。建议{'安排面试' if passed > 0 else '暂不推进'}。"

    def _evaluate_recommendation(self, matches: list[PositionMatchItem]) -> bool:
        if not matches:
            return False
        best = matches[0]
        if best.finalScore and best.finalScore >= SCREENING_THRESHOLD:
            return True
        above_threshold = sum(1 for m in matches if m.finalScore and m.finalScore >= 50)
        return above_threshold >= 2

    @staticmethod
    def _build_position_content(position: Position) -> str:
        parts = [
            f"岗位: {position.title}",
            f"公司: {position.company or ''}",
            f"经验要求: {position.experience or ''}",
            f"学历要求: {position.education or ''}",
            f"岗位职责: {position.responsibilities or ''}",
            f"任职要求: {position.requirements or ''}",
        ]
        if position.skills:
            parts.append(f"技能要求: {', '.join(position.skills)}")
        return "\n".join(parts)

    @staticmethod
    def _calculate_grade(score: float) -> str:
        if score >= 85: return "A"
        if score >= 70: return "B"
        if score >= 50: return "C"
        return "D"

    @staticmethod
    def _calculate_recommend_level(score: float) -> int:
        if score >= 90: return 5
        if score >= 75: return 4
        if score >= 60: return 3
        if score >= 45: return 2
        return 1
