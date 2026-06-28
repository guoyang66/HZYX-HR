"""
面试记录模型 - AI生成的面试题存储
"""
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class InterviewRecord(Base):
    """面试题记录表 - 存储AI生成的面试题目及参考答案"""
    __tablename__ = "interview_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    position_id: Mapped[int | None] = mapped_column(nullable=True)        # 关联岗位ID（可为空）
    user_id: Mapped[int] = mapped_column(nullable=False)                  # 生成者ID
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)    # 难度：JUNIOR/MIDDLE/SENIOR
    question_type: Mapped[str | None] = mapped_column(String(20), nullable=True) # 题目类型：TECHNICAL/BEHAVIORAL/SCENARIO/MIXED
    questions: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)   # JSONB格式的题目列表
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
