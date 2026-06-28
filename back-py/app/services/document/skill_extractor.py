"""
技能提取器 - 从简历文本中提取技术技能（知识图谱 + AI + 正则三层级兜底）
"""
import logging
import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.graph.skill_graph import SkillGraphService
from app.services.ai.router import model_router

logger = logging.getLogger(__name__)


class SkillExtractor:
    """技能提取器 - 三级降级策略：图谱提取 -> AI提取 -> 正则兜底"""

    async def extract_skills(self, content: str, user_id: int, db: AsyncSession) -> list[str]:
        """从简历原文中提取技能列表，按优先级逐级尝试"""
        if not content:
            return []

        extracted = set()

        # 第一级：知识图谱提取（无需AI，始终可用）
        try:
            graph_service = SkillGraphService()
            graph_based = await graph_service.extract_skills(content)
            extracted.update(graph_based)
        except Exception as e:
            logger.warning("Graph skill extraction failed: %s", str(e))

        # 图谱已找到技能时跳过AI提取（提升速度）
        if extracted:
            return list(extracted)

        # 第二级：AI智能提取（需要AI模型可用）
        try:
            ai_extracted = await self._extract_with_ai(content, user_id)
            extracted.update(ai_extracted)
        except Exception as e:
            logger.info("AI skill extraction skipped (AI may be unavailable): %s", str(e))
            # 第三级：正则表达式兜底（匹配常见技术关键词）
            if not extracted:
                extracted.update(self._regex_extract(content))

        return list(extracted)

    @staticmethod
    def _regex_extract(content: str) -> set[str]:
        """最后兜底手段——正则匹配常见技术技能关键词"""
        common_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
            "Docker", "Kubernetes", "AWS", "Azure", "Linux",
            "React", "Vue", "Angular", "Node.js", "Spring", "Django", "FastAPI",
            "Git", "CI/CD", "REST API", "GraphQL", "Microservices",
            "Machine Learning", "AI", "Data Analysis",
        ]
        found = set()
        lower = content.lower()
        for skill in common_skills:
            if skill.lower() in lower:
                found.add(skill)
        return found

    async def _extract_with_ai(self, content: str, user_id: int) -> list[str]:
        """调用AI模型从简历原文中智能提取技能"""
        prompt = f"""请从以下简历内容中提取技术技能和软技能。
只返回技能名称列表，用逗号分隔，不要包含其他内容。

简历内容：
{self._truncate_content(content, 2000)}

提取的技能（用逗号分隔）："""

        messages = [{"role": "user", "content": prompt}]
        adapter = model_router.route(user_id)
        response = await adapter.chat(messages)

        skills = []
        for part in re.split(r'[,，、]', response):
            s = part.strip()
            if s and len(s) <= 50:
                skills.append(s)
        return skills

    @staticmethod
    def _truncate_content(content: str, max_length: int) -> str:
        """截断文本以避免超出AI token限制"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    async def normalize_skills(self, skills: list[str]) -> list[str]:
        """技能标准化——将提取的技能名称对齐到知识图谱中的标准名称"""
        if not skills:
            return []
        normalized = []
        seen = set()
        graph_service = SkillGraphService()
        for skill in skills:
            # 先按名称精确匹配
            found = await graph_service.find_by_name(skill)
            if found:
                name = found.get("name", skill)
                if name not in seen:
                    normalized.append(name)
                    seen.add(name)
            else:
                # 再按关键词模糊匹配
                by_keyword = await graph_service.find_by_keyword(skill)
                if by_keyword:
                    name = by_keyword.get("name", skill)
                    if name not in seen:
                        normalized.append(name)
                        seen.add(name)
                else:
                    if skill not in seen:
                        normalized.append(skill)
                        seen.add(skill)
        return normalized
