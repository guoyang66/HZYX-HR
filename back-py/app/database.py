"""
数据库层 - SQLAlchemy 2.0 异步引擎、会话管理、ORM基类
使用 asyncpg 驱动连接 PostgreSQL，支持连接池和自动建表
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 异步数据库引擎 - 连接池大小10，连接回收时间300秒
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,        # 调试模式下打印SQL语句
    pool_size=10,               # 连接池大小
    max_overflow=0,             # 不额外溢出
    pool_recycle=300,           # 连接回收时间（秒）
)

# 异步会话工厂 - 每次请求创建新会话，提交后不保持对象过期状态
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基类，所有模型继承自此类"""
    pass


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入：获取数据库会话，异常时自动回滚，正常时自动提交"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """应用启动时创建所有数据库表（如果不存在）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
