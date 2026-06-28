"""
技能知识图谱服务 - 基于 Neo4j 图数据库的技能匹配与提取
核心功能：从知识图谱中提取技能节点、计算候选人技能与岗位要求的匹配度
"""
import re
import logging
from neo4j import GraphDatabase
from app.config import settings

logger = logging.getLogger(__name__)


class SkillGraphService:
    """技能知识图谱服务 - 连接Neo4j，执行Cypher查询，实现技能匹配"""

    def __init__(self):
        self._driver = None
        try:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_lifetime=30,
            )
        except Exception as e:
            logger.warning("Neo4j connection failed: %s. Graph features disabled.", str(e))

    def _run_query(self, query: str, params: dict = None) -> list[dict]:
        """执行 Cypher 查询，返回字典列表。连接不可用时返回空列表"""
        if not self._driver:
            return []
        try:
            with self._driver.session() as session:
                result = session.run(query, params or {})
                return [dict(record) for record in result]
        except Exception as e:
            logger.warning("Neo4j query failed: %s", str(e))
            return []

    async def extract_skills(self, content: str) -> list[str]:
        """从文本内容中提取技能——遍历图谱中所有技能节点，检查是否出现在文本中"""
        if not content:
            return []
        skills = []
        lower_content = content.lower()
        all_skills = await self.get_all_skills()

        for skill in all_skills:
            name = skill.get("name", "")
            # 精确匹配技能名称
            if self._contains_skill(lower_content, name):
                skills.append(name)
                continue
            # 模糊匹配技能关键词
            keywords = skill.get("keywords", [])
            if keywords:
                for kw in keywords:
                    if self._contains_skill(lower_content, kw):
                        skills.append(name)
                        break

        return list(set(skills))

    async def calculate_skill_match(self, candidate_skills: list[str], position_skills: list[str]) -> dict:
        """快速技能匹配——基于名称直接比较（前缀/后缀匹配），不依赖Neo4j查询"""
        candidate_lower = {s.lower(): s for s in candidate_skills}
        position_lower = {s.lower(): s for s in position_skills}

        if not position_lower:
            return {"score": 0.0, "matchedSkills": [], "missingSkills": [], "extraSkills": list(candidate_skills)}

        matched = []
        missing = []
        for pl, p in position_lower.items():
            found = pl in candidate_lower
            # 也支持前缀/后缀子串匹配
            if not found:
                for cl in candidate_lower:
                    if cl in pl or pl in cl:
                        found = True
                        break
            if found:
                matched.append(p)
            else:
                missing.append(p)

        extra = [s for s in candidate_skills if s.lower() not in position_lower]

        # 匹配得分 = 匹配技能数 / 岗位要求技能数
        score = len(matched) / len(position_lower) if position_lower else 0.0

        return {
            "score": round(score, 4),
            "matchedSkills": matched,
            "missingSkills": missing,
            "extraSkills": extra,
        }

    async def get_all_skills(self) -> list[dict]:
        """获取知识图谱中所有技能节点"""
        query = "MATCH (s:Skill) RETURN s.name as name, s.keywords as keywords, s.level as level, s.description as description"
        return self._run_query(query)

    async def find_by_name(self, name: str) -> dict | None:
        """按名称精确查找技能节点"""
        query = "MATCH (s:Skill {name: $name}) RETURN s.name as name, s.keywords as keywords, s.level as level"
        results = self._run_query(query, {"name": name})
        return results[0] if results else None

    async def find_by_keyword(self, keyword: str) -> dict | None:
        """按关键词模糊查找技能节点（忽略大小写）"""
        query = """
        MATCH (s:Skill)
        WHERE ANY(k IN s.keywords WHERE toLower(k) CONTAINS toLower($keyword))
        RETURN s.name as name, s.keywords as keywords, s.level as level
        LIMIT 1
        """
        results = self._run_query(query, {"keyword": keyword})
        return results[0] if results else None

    async def get_skill_count(self) -> int:
        """获取技能节点总数"""
        results = self._run_query("MATCH (s:Skill) RETURN count(s) as count")
        return results[0]["count"] if results else 0

    @staticmethod
    def _contains_skill(content: str, skill: str) -> bool:
        """检查文本中是否包含某个技能（正则全词匹配 + 子串匹配）"""
        if not skill:
            return False
        lower_skill = skill.lower()
        # 优先正则全词匹配
        pattern = re.compile(r'(?i)\b' + re.escape(lower_skill) + r'\b')
        if pattern.search(content):
            return True
        # 兜底子串匹配（如 "Node.js" 中的 "node"）
        return lower_skill in content
