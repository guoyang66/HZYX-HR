"""
简历模型 - 上传的简历解析结果存储
"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Resume(Base):
    """简历表 - 存储上传简历的文件信息和AI解析结果"""
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False)              # 上传者ID
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)   # 原始文件名
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)   # 服务器存储路径
    content: Mapped[str | None] = mapped_column(Text, nullable=True)            # 解析后的文本内容
    extracted_skills: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)  # AI提取的技能列表
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
