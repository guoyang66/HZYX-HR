"""
用户模型 - 系统用户（HR/面试官）的数据库映射
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Enum as SAEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UserRole(str, Enum):
    """用户角色枚举"""
    HR = "HR"                    # HR：管理简历、岗位、匹配
    INTERVIEWER = "INTERVIEWER"  # 面试官：生成面试题


class User(Base):
    """用户表 - 存储HR和面试官账号信息"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)    # bcrypt 加密存储
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="HR")  # 用户角色
    preferred_model: Mapped[str] = mapped_column(String(50), default="aliyun")   # 首选AI模型
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
