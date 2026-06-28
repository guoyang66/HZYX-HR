"""
匹配记录模型 - 简历与岗位的匹配分析结果存储
"""
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MatchRecord(Base):
    """匹配记录表 - 存储每次匹配分析的各项得分和详细报告"""
    __tablename__ = "match_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(nullable=False)         # 关联简历ID
    position_id: Mapped[int] = mapped_column(nullable=False)       # 关联岗位ID
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)    # 综合匹配得分（0-100）
    rag_score: Mapped[float | None] = mapped_column(Float, nullable=True)      # RAG检索得分（暂未启用）
    graph_score: Mapped[float | None] = mapped_column(Float, nullable=True)    # 知识图谱技能匹配得分
    llm_score: Mapped[float | None] = mapped_column(Float, nullable=True)      # LLM综合评估得分
    matched_skills: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)   # 匹配上的技能
    missing_skills: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)   # 缺失的技能
    llm_report: Mapped[str | None] = mapped_column(Text, nullable=True)                    # LLM生成的评估报告
    matched_by: Mapped[int | None] = mapped_column(nullable=True)                          # 执行匹配的用户ID
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
