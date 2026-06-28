"""
混合匹配服务 - 结合知识图谱技能匹配 + LLM综合评估，加权计算综合得分
匹配策略：50% 知识图谱 + 50% LLM评估，根据得分映射评级（A/B/C/D）和推荐星级
"""
import json
import logging
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.graph.skill_graph import SkillGraphService
from app.services.ai.router import model_router

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """匹配结果数据类 - 包含各项得分和技能分析"""
    resume_id: int = 0
    position_id: int = 0
    final_score: float = 0.0      # 综合得分（0-100）
    rag_score: float = 0.0        # RAG检索得分（暂未启用）
    graph_score: float = 0.0      # 知识图谱技能匹配得分（0-100）
    llm_score: float = 0.0        # LLM综合评估得分（0-100）
    matched_skills: list[str] = field(default_factory=list)   # 匹配上的技能列表
    missing_skills: list[str] = field(default_factory=list)   # 候选人缺失的技能
    extra_skills: list[str] = field(default_factory=list)     # 候选人额外掌握的技能
    llm_report: str = ""          # LLM生成的文字评估报告
    score_details: dict = field(default_factory=dict)         # 得分明细
    recommend_level: int = 1      # 推荐星级（1-5）
    match_grade: str = "D"        # 匹配等级（A/B/C/D）


class HybridMatchService:
    """混合匹配服务 - 综合图谱匹配和AI评估，给出智能人岗匹配结果"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._graph_service = SkillGraphService()

    async def match(
        self,
        resume_content: str,
        resume_skills: list[str],
        position_content: str,
        position_skills: list[str],
        user_id: int,
    ) -> MatchResult:
        """执行混合匹配：先图谱技能匹配(50%)，再LLM综合评估(50%)，加权合并"""
        # RAG匹配暂未启用（与Java版本保持一致）
        rag_score = 0.0

        # 第一步：知识图谱技能匹配（权重0.5）
        graph_result = await self._graph_service.calculate_skill_match(resume_skills, position_skills)
        graph_score = graph_result.get("score", 0.0)

        # 第二步：LLM综合评估（权重0.5）
        try:
            llm_eval = await self._llm_evaluate(resume_content, resume_skills, position_content, position_skills, graph_result, user_id)
            llm_score = llm_eval.get("score", 0.0) / 100.0
            llm_report = llm_eval.get("report", "")
        except Exception as e:
            # AI不可用时降级为纯图谱评估
            logger.info("LLM evaluation skipped: %s. Using graph-only score.", str(e))
            llm_score = graph_score
            llm_report = f"基于知识图谱技能匹配评估。匹配度: {graph_score:.0%}。匹配技能: {', '.join(graph_result.get('matchedSkills', []))}。缺失技能: {', '.join(graph_result.get('missingSkills', []))}"

        # 综合得分 = 0.5 * 图谱 + 0.5 * LLM，归一化到0-100
        final_score = round((0.5 * graph_score + 0.5 * llm_score) * 100, 1)

        return MatchResult(
            final_score=final_score,
            rag_score=rag_score,
            graph_score=round(graph_score * 100, 1),
            llm_score=round(llm_score * 100, 1),
            matched_skills=graph_result.get("matchedSkills", []),
            missing_skills=graph_result.get("missingSkills", []),
            extra_skills=graph_result.get("extraSkills", []),
            llm_report=llm_report,
            score_details={
                "graphScore": round(graph_score * 100, 1),
                "llmScore": round(llm_score * 100, 1),
                "weights": {"graph": 0.5, "llm": 0.5},
            },
            recommend_level=self._calculate_recommend_level(final_score),
            match_grade=self._calculate_grade(final_score),
        )

    async def _llm_evaluate(
        self,
        resume_content: str,
        resume_skills: list[str],
        position_content: str,
        position_skills: list[str],
        graph_result: dict,
        user_id: int,
    ) -> dict:
        """调用AI模型进行综合评估，返回JSON格式的分数和评语"""
        try:
            adapter = model_router.route(user_id)
            if not adapter.is_enabled():
                raise RuntimeError("No AI model enabled")
        except Exception as e:
            raise RuntimeError(f"AI model unavailable: {e}")

        # 构造精简Prompt以加快评估速度
        prompt = f"""评估候选人与岗位匹配度（0-100分），返回JSON: {{"score": 分数, "report": "简短评估"}}

岗位: {position_content[:500]}
候选人技能: {', '.join(resume_skills[:10])}
岗位要求: {', '.join(position_skills[:10])}
图谱匹配: {graph_result.get('score', 0):.0%}"""

        messages = [{"role": "user", "content": prompt}]
        response = await adapter.chat(messages)

        # 从AI返回中提取JSON
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except (json.JSONDecodeError, ValueError):
            pass

        return {"score": int(graph_result.get("score", 0) * 100), "report": response[:200]}

    @staticmethod
    def _calculate_grade(score: float) -> str:
        """根据得分计算匹配等级：A(>=85) B(>=70) C(>=50) D(<50)"""
        if score >= 85:
            return "A"
        if score >= 70:
            return "B"
        if score >= 50:
            return "C"
        return "D"

    @staticmethod
    def _calculate_recommend_level(score: float) -> int:
        """根据得分计算推荐星级：>=90五颗星 >=75四星 >=60三星 >=45二星 <45一星"""
        if score >= 90:
            return 5
        if score >= 75:
            return 4
        if score >= 60:
            return 3
        if score >= 45:
            return 2
        return 1
