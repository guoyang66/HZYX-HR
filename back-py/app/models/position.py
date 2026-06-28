"""
岗位模型 - 招聘岗位/职位的数据库映射
"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Position(Base):
    """岗位表 - 存储招聘岗位的详细信息和技能要求"""
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)        # 岗位名称
    company: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 公司名称
    salary_range: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 薪资范围
    experience: Mapped[str | None] = mapped_column(String(50), nullable=True)    # 经验要求
    education: Mapped[str | None] = mapped_column(String(50), nullable=True)     # 学历要求
    location: Mapped[str | None] = mapped_column(String(50), nullable=True)      # 工作地点
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)    # 岗位职责
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)        # 任职要求
    skills: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True) # 技能标签列表
    created_by: Mapped[int | None] = mapped_column(nullable=True)                # 创建者ID
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")  # 软删除标记
