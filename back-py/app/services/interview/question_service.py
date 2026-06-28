"""
面试题生成服务 - 基于AI的智能面试题生成（支持技术/行为/情景题，初中高难度）
当AI不可用时降级为模板生成
"""
import json
import logging
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.interview_record import InterviewRecord
from app.models.position import Position
from app.schemas.interview import GenerateQuestionsRequest, InterviewRecordDTO, InterviewQuestionDTO
from app.api.exception_handlers import BusinessException
from app.services.ai.router import model_router

logger = logging.getLogger(__name__)


class InterviewQuestionService:
    """面试题服务 - AI生成面试题并持久化，支持按岗位/按技能/指定参数生成"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_questions(self, request: GenerateQuestionsRequest, user_id: int) -> InterviewRecordDTO:
        """核心生成方法：根据请求参数生成面试题并保存"""
        skills = request.skills or []
        position_title = None

        # 如果指定了岗位ID，从数据库读取岗位信息作为上下文
        if request.positionId:
            result = await self.db.execute(select(Position).where(Position.id == request.positionId, Position.deleted == False))
            position = result.scalar_one_or_none()
            if position:
                position_title = position.title
                if not skills:
                    skills = position.skills or []
                context = f"岗位名称: {position.title}\n岗位职责: {position.responsibilities or ''}\n岗位要求: {position.requirements or ''}"
            else:
                context = None
        else:
            context = None

        if not skills:
            raise BusinessException("请指定岗位或技能列表")

        # AI生成（不可用时自动降级为模板生成）
        questions = await self._generate_with_ai(
            skills=skills,
            difficulty=request.difficulty,
            count=request.count,
            question_type=request.questionType,
            include_answers=request.includeAnswers,
            business_domain=request.businessDomain,
            position_context=context or "",
            user_id=user_id,
        )

        # 保存面试题记录
        record = InterviewRecord(
            position_id=request.positionId,
            user_id=user_id,
            difficulty=request.difficulty,
            question_type=request.questionType,
            questions=[q.model_dump() for q in questions],
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(record)
        await self.db.flush()

        return self._to_dto(record, position_title)

    async def generate_by_position(self, position_id: int, difficulty: str | None, count: int, user_id: int) -> InterviewRecordDTO:
        """快捷方法：按岗位生成面试题"""
        request = GenerateQuestionsRequest(
            positionId=position_id,
            difficulty=difficulty or "MIDDLE",
            count=count,
        )
        return await self.generate_questions(request, user_id)

    async def generate_by_skills(self, skills: list[str], difficulty: str | None, count: int, user_id: int) -> InterviewRecordDTO:
        """快捷方法：按技能列表生成面试题"""
        request = GenerateQuestionsRequest(
            skills=skills,
            difficulty=difficulty or "MIDDLE",
            count=count,
        )
        return await self.generate_questions(request, user_id)

    async def get_record(self, record_id: int) -> InterviewRecordDTO:
        """获取单条面试题记录"""
        result = await self.db.execute(select(InterviewRecord).where(InterviewRecord.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise BusinessException("面试记录不存在", 404)
        position_title = await self._get_position_title(record.position_id)
        return self._to_dto(record, position_title)

    async def list_records(self, user_id: int, page: int, size: int) -> dict:
        """分页查询当前用户的面试题记录"""
        count_query = select(func.count()).select_from(InterviewRecord).where(InterviewRecord.user_id == user_id)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = select(InterviewRecord).where(InterviewRecord.user_id == user_id).offset(page * size).limit(size).order_by(InterviewRecord.created_at.desc())
        result = await self.db.execute(query)
        records = result.scalars().all()

        dto_list = []
        for r in records:
            position_title = await self._get_position_title(r.position_id)
            dto_list.append(self._to_dto(r, position_title))

        return {
            "content": dto_list,
            "totalElements": total,
            "totalPages": max(1, (total + size - 1) // size),
            "number": page,
            "size": size,
        }

    async def delete_record(self, record_id: int, user_id: int):
        """删除面试题记录（需权限校验）"""
        result = await self.db.execute(select(InterviewRecord).where(InterviewRecord.id == record_id, InterviewRecord.user_id == user_id))
        record = result.scalar_one_or_none()
        if not record:
            raise BusinessException("面试记录不存在", 404)
        await self.db.delete(record)
        await self.db.flush()

    async def _generate_with_ai(
        self,
        skills: list[str],
        difficulty: str,
        count: int,
        question_type: str,
        include_answers: bool,
        business_domain: str,
        position_context: str,
        user_id: int,
    ) -> list[InterviewQuestionDTO]:
        """调用AI生成面试题，失败时降级为模板生成"""
        difficulty_map = {"JUNIOR": "初级", "MIDDLE": "中级", "SENIOR": "高级"}
        diff_cn = difficulty_map.get(difficulty, "中级")

        type_guide = {
            "TECHNICAL": "仅生成技术类题目（算法、框架、原理等）",
            "BEHAVIORAL": "仅生成行为类题目（团队合作、冲突处理等）",
            "SCENARIO": "仅生成情景类题目（实际工作场景模拟）",
            "MIXED": "混合生成技术题、行为题和情景题",
        }
        type_desc = type_guide.get(question_type, "混合生成各类题目")

        answer_instruction = "请包含参考答案要点。" if include_answers else "不需要包含答案。"

        # 构造面试题生成Prompt
        prompt = f"""你是一位资深技术面试官。请为以下岗位生成{diff_cn}难度的面试题。

业务领域: {business_domain}
技能要求: {', '.join(skills)}
难度: {diff_cn}
题目数量: {count}道
题目类型要求: {type_desc}
{answer_instruction}

{position_context}

请以JSON数组格式返回，每个元素包含以下字段：
- question: 题目内容
- type: 题目类型（TECHNICAL/BEHAVIORAL/SCENARIO）
- difficulty: 难度（JUNIOR/MIDDLE/SENIOR）
- skill: 考察的主要技能
- answerPoints: 参考答案要点（如果要求包含答案）
- evaluationDimension: 评估维度

只返回JSON数组，不要包含其他内容。"""

        messages = [{"role": "user", "content": prompt}]

        try:
            adapter = model_router.route(user_id)
            response = await adapter.chat(messages)

            # 从AI响应中提取JSON数组
            try:
                json_start = response.find("[")
                json_end = response.rfind("]") + 1
                if json_start >= 0 and json_end > json_start:
                    questions_data = json.loads(response[json_start:json_end])
                    return [InterviewQuestionDTO(**q) for q in questions_data[:count]]
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
        except Exception as e:
            logger.info("AI question generation unavailable (%s), using default templates", str(e))

        # AI不可用时降级为模板生成
        return self._generate_default_questions(skills, difficulty, count, question_type)

    def _generate_default_questions(self, skills: list[str], difficulty: str, count: int, question_type: str) -> list[InterviewQuestionDTO]:
        """降级方案：使用预设模板生成面试题"""
        templates = {
            "JUNIOR": [
                "请简述{skill}的基本概念和应用场景。",
                "{skill}中常见的坑有哪些？如何避免？",
                "请描述{skill}的核心原理。",
            ],
            "MIDDLE": [
                "请深入分析{skill}的底层实现机制。",
                "{skill}在分布式系统中的应用和挑战是什么？",
                "请对比{skill}与其他类似技术的优缺点。",
                "如何在项目中优化{skill}的性能？",
            ],
            "SENIOR": [
                "请设计一个基于{skill}的高可用架构方案。",
                "{skill}在百万级并发场景下如何调优？",
                "从零到一构建{skill}系统，你会如何设计技术选型？",
                "请分析{skill}的技术演进趋势和未来方向。",
            ],
        }

        diff_templates = templates.get(difficulty, templates["MIDDLE"])
        questions = []
        for i in range(min(count, len(skills) * len(diff_templates))):
            skill = skills[i % len(skills)]
            template = diff_templates[i % len(diff_templates)]
            q_type = "TECHNICAL"
            if question_type == "BEHAVIORAL":
                q_type = "BEHAVIORAL"
            elif question_type == "SCENARIO":
                q_type = "SCENARIO"

            questions.append(InterviewQuestionDTO(
                question=template.format(skill=skill),
                type=q_type,
                difficulty=difficulty,
                skill=skill,
                answerPoints="请根据实际项目经验回答",
                evaluationDimension=f"{skill}掌握程度",
            ))
        return questions

    async def _get_position_title(self, position_id: int | None) -> str | None:
        """获取岗位名称（用于前端展示）"""
        if not position_id:
            return None
        result = await self.db.execute(select(Position).where(Position.id == position_id))
        position = result.scalar_one_or_none()
        return position.title if position else None

    def _to_dto(self, record: InterviewRecord, position_title: str | None) -> InterviewRecordDTO:
        """ORM转为DTO"""
        questions = []
        if record.questions:
            questions = [InterviewQuestionDTO(**q) for q in record.questions]
        return InterviewRecordDTO(
            id=record.id,
            positionId=record.position_id,
            positionTitle=position_title,
            userId=record.user_id,
            difficulty=record.difficulty,
            questionType=record.question_type,
            questions=questions,
            createdAt=record.created_at,
        )
