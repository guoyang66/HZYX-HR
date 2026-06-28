"""
Match Analysis LangGraph Workflow
Orchestrates the multi-step resume-to-position matching process:
1. Parse resume → 2. Extract skills → 3. Vector search → 4. Graph analysis → 5. LLM scoring
"""
import logging
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from app.services.graph.skill_graph import SkillGraphService
from app.services.ai.router import model_router

logger = logging.getLogger(__name__)


class MatchState(TypedDict):
    resume_content: str
    resume_skills: list[str]
    position_content: str
    position_skills: list[str]
    user_id: int
    # Intermediate results
    extracted_skills: list[str]
    graph_score: float
    llm_score: float
    llm_report: str
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]
    # Final result
    final_score: float
    match_grade: str
    recommend_level: int


class MatchWorkflow:
    """LangGraph workflow for hybrid resume-position matching"""
    
    def __init__(self):
        self.graph = self._build_graph()
        self._graph_service = SkillGraphService()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(MatchState)

        workflow.add_node("extract_skills", self._extract_skills_node)
        workflow.add_node("graph_analysis", self._graph_analysis_node)
        workflow.add_node("llm_evaluation", self._llm_evaluation_node)
        workflow.add_node("calculate_final", self._calculate_final_node)

        workflow.set_entry_point("extract_skills")
        workflow.add_edge("extract_skills", "graph_analysis")
        workflow.add_edge("graph_analysis", "llm_evaluation")
        workflow.add_edge("llm_evaluation", "calculate_final")
        workflow.add_edge("calculate_final", END)

        return workflow.compile()

    async def _extract_skills_node(self, state: MatchState) -> dict:
        """Node 1: Extract skills from resume content"""
        logger.debug("Match workflow: extracting skills")
        # Skills already extracted from resume: state.get("resume_skills", [])
        return {"extracted_skills": state.get("resume_skills", [])}

    async def _graph_analysis_node(self, state: MatchState) -> dict:
        """Node 2: Knowledge graph skill matching"""
        logger.debug("Match workflow: graph analysis")
        candidate_skills = state.get("extracted_skills", [])
        position_skills = state.get("position_skills", [])

        result = await self._graph_service.calculate_skill_match(candidate_skills, position_skills)

        return {
            "graph_score": result.get("score", 0.0),
            "matched_skills": result.get("matchedSkills", []),
            "missing_skills": result.get("missingSkills", []),
            "extra_skills": result.get("extraSkills", []),
        }

    async def _llm_evaluation_node(self, state: MatchState) -> dict:
        """Node 3: LLM comprehensive evaluation"""
        logger.debug("Match workflow: LLM evaluation")
        try:
            prompt = f"""你是一位资深的HR招聘专家。请根据以下信息，对候选人与岗位的匹配程度进行全面评估。

岗位描述：
{state.get("position_content", "")}

候选人简历摘要：
{state.get("resume_content", "")[:1500]}

技能匹配分析：
- 匹配技能: {', '.join(state.get("matched_skills", []))}
- 缺失技能: {', '.join(state.get("missing_skills", []))}
- 额外技能: {', '.join(state.get("extra_skills", []))}

请给出0-100的匹配评分和简短评估报告。格式：score|report"""
            adapter = model_router.route(state.get("user_id", None))
            response = await adapter.chat([{"role": "user", "content": prompt}])

            parts = response.split("|", 1)
            score = float(parts[0].strip()) if parts else 50.0
            report = parts[1].strip() if len(parts) > 1 else response[:200]

            return {"llm_score": score / 100.0, "llm_report": report}
        except Exception as e:
            logger.warning("LLM evaluation failed in workflow: %s", str(e))
            return {"llm_score": state.get("graph_score", 0.0), "llm_report": "LLM评估不可用"}

    async def _calculate_final_node(self, state: MatchState) -> dict:
        """Node 4: Calculate final combined score"""
        graph_score = state.get("graph_score", 0.0)
        llm_score = state.get("llm_score", 0.0)
        final_score = round((0.5 * graph_score + 0.5 * llm_score) * 100, 1)

        grade = "D"
        if final_score >= 85: grade = "A"
        elif final_score >= 70: grade = "B"
        elif final_score >= 50: grade = "C"

        level = 1
        if final_score >= 90: level = 5
        elif final_score >= 75: level = 4
        elif final_score >= 60: level = 3
        elif final_score >= 45: level = 2

        return {"final_score": final_score, "match_grade": grade, "recommend_level": level}

    async def run(self, initial_state: MatchState) -> MatchState:
        """Execute the match workflow"""
        result = await self.graph.ainvoke(initial_state)
        return result
