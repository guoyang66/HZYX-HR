"""
认证API路由 - 登录、注册、Token刷新、获取当前用户
对应 Java 版本: AuthController.java
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth import AuthService
from app.api.deps import get_current_user, get_optional_user
from app.models.user import User

router = APIRouter()


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录：验证用户名密码，返回访问令牌和刷新令牌"""
    auth_service = AuthService(db)
    result = await auth_service.login(request)
    return ApiResponse.success(result.model_dump(), "登录成功")


@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册：创建账户（HR或面试官角色）"""
    auth_service = AuthService(db)
    result = await auth_service.register(request)
    return ApiResponse.success(result.model_dump(), "注册成功")


@router.post("/refresh")
async def refresh_token(refreshToken: str, db: AsyncSession = Depends(get_db)):
    """刷新令牌：用refresh token换取新的access和refresh token"""
    auth_service = AuthService(db)
    result = await auth_service.refresh_token(refreshToken)
    return ApiResponse.success(result.model_dump(), "Token 刷新成功")


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的信息（需携带Token）"""
    user_info = AuthService.get_current_user_info(current_user)
    return ApiResponse.success(user_info.model_dump())


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """退出登录（前端清除Token即可，后端仅返回成功）"""
    return ApiResponse.success_message("登出成功")
