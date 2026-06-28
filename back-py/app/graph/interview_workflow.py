
import json
import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.services.ai.router import model_router
from app.services.interview.question_bank import QuestionBankService

logger = logging.getLogger(__name__)


class InterviewState(TypedDict):
    skills: list[str]
    difficulty: str
    count: int
    question_type: str
    include_answers: bool
    business_domain: str
    position_context: str
    user_id: int
    # Intermediate
    similar_questions: list[dict]
    questions: list[dict]
    # Final
    generated_questions: list[dict]


class InterviewWorkflow:
    """LangGraph workflow for AI-powered interview question generation"""

    def __init__(self):
        self.graph = self._build_graph()
        self._question_bank = QuestionBankService()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(InterviewState)

        workflow.add_node("search_bank", self._search_question_bank_node)
        workflow.add_node("generate_ai", self._generate_ai_node)
        workflow.add_node("validate", self._validate_node)

        workflow.set_entry_point("search_bank")
        workflow.add_edge("search_bank", "generate_ai")
        workflow.add_edge("generate_ai", "validate")
        workflow.add_edge("validate", END)

        return workflow.compile()

    async def _search_question_bank_node(self, state: InterviewState) -> dict:
        """Node 1: Search internal question bank for similar questions"""
        logger.debug("Interview workflow: searching question bank")
        query = f"{' '.join(state.get('skills', []))} {state.get('difficulty', '')} {state.get('business_domain', '')}"
        results = await self._question_bank.search_similar_questions(query, top_k=5)
        return {"similar_questions": results}

    async def _generate_ai_node(self, state: InterviewState) -> dict:
        """Node 2: Generate questions using AI"""
        logger.debug("Interview workflow: generating questions with AI")

        bank_context = self._question_bank.format_results_as_context(state.get("similar_questions", []))

        prompt = f"""你是一位资深技术面试官。请根据以下信息生成面试题。

业务领域: {state.get("business_domain", "企业金融/支付")}
技能要求: {', '.join(state.get('skills', []))}
难度: {state.get('difficulty', 'MIDDLE')}
数量: {state.get('count', 5)}道
{bank_context}

请以JSON数组格式返回面试题，每个元素包含：
- question: 题目内容
- type: TECHNIICAL/BEHAVIORAL/SCENARIO
- difficulty: 难度
- skill: 主要技能
- answerPoints: 参考答案
- evaluationDimension: 评估维度

只返回JSON数组。"""

        try:
            adapter = model_router.route(state.get("user_id", None))
            response = await adapter.chat([{"role": "user", "content": prompt}])

            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                questions = json.loads(response[json_start:json_end])
                return {"questions": questions[:state.get("count", 5)]}
        except Exception as e:
            logger.warning("AI question generation failed in workflow: %s", str(e))

        return {"questions": []}

    async def _validate_node(self, state: InterviewState) -> dict:
        """Node 3: Validate and filter generated questions"""
        logger.debug("Interview workflow: validating questions")
        questions = state.get("questions", [])
        valid = [q for q in questions if q.get("question") and len(q.get("question", "")) > 5]
        return {"generated_questions": valid}

    async def run(self, initial_state: InterviewState) -> InterviewState:
        """Execute the interview generation workflow"""
        result = await self.graph.ainvoke(initial_state)
        return result
