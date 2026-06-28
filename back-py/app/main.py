"""
应用主入口 - FastAPI 应用启动、中间件注册、路由挂载、生命周期管理
对应 Java 版本: SmartHrApplication.java
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)-5s %(name)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化数据库表和AI模型适配器"""
    await init_db()
    _init_ai_adapters()
    yield


def _init_ai_adapters():
    """启动时初始化并注册AI模型适配器（阿里云百炼/OpenAI），根据配置自动启用可用模型"""
    from app.services.ai.registry import model_registry
    try:
        from app.services.ai.aliyun import AliyunAdapter
        aliyun = AliyunAdapter()
        if aliyun.is_enabled():
            model_registry.register(aliyun)
    except Exception as e:
        logging.warning("Failed to init Aliyun adapter: %s", e)

    try:
        from app.services.ai.openai_adapter import OpenAIAdapter
        openai = OpenAIAdapter()
        if openai.is_enabled():
            model_registry.register(openai)
    except Exception as e:
        logging.warning("Failed to init OpenAI adapter: %s", e)

    enabled = model_registry.get_enabled_model_ids()
    logging.info("Initialized AI adapters: %s", enabled if enabled else "none")


app = FastAPI(
    title="Smart HR API",
    version="v1",
    description="HZYX-HR 智能招聘匹配助手后端服务 (Python/LangChain/LangGraph)",
    docs_url="/swagger-ui.html",
    openapi_url="/v3/api-docs",
    lifespan=lifespan,
)

# 跨域配置 - 允许前端开发服务器(localhost:3000)访问后端API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
    max_age=3600,
)

# 导入并注册各业务模块的路由
from app.api.auth import router as auth_router
from app.api.ai import router as ai_router
from app.api.hr.positions import router as position_router
from app.api.hr.resumes import router as resume_router
from app.api.hr.matches import router as match_router
from app.api.interview import router as interview_router
from app.api.boss import router as boss_router

app.include_router(auth_router, prefix="/api/auth", tags=["认证管理"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI模型管理"])
app.include_router(position_router, prefix="/api/hr/positions", tags=["岗位管理"])
app.include_router(resume_router, prefix="/api/hr/resumes", tags=["简历管理"])
app.include_router(match_router, prefix="/api/hr/match", tags=["匹配分析"])
app.include_router(interview_router, prefix="/api/interview", tags=["面试题管理"])
app.include_router(boss_router, prefix="/api/webhook/boss", tags=["Boss直聘集成"])


# 注册全局异常处理器（业务异常、验证异常、通用异常）
from app.api.exception_handlers import (
    BusinessException,
    business_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/actuator/health")
async def health_check():
    """健康检查端点，用于监控和容器探活"""
    return {"status": "UP"}
