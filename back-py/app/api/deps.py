"""
认证依赖模块 - JWT令牌验证、用户身份获取、角色访问控制
对应 Java 版本: Spring Security + JWT AuthenticationFilter + @PreAuthorize
提供 FastAPI 依赖注入式的认证和授权机制
"""
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models.user import User

# HTTP Bearer Token 认证方案
security = HTTPBearer()


def decode_jwt(token: str) -> dict:
    """解码JWT令牌，校验签名和有效期"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的Token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """核心认证依赖：从请求头提取JWT，解析用户信息，返回当前登录用户。
    所有需要登录的接口都应该声明 `current_user: User = Depends(get_current_user)`"""
    payload = decode_jwt(credentials.credentials)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token无效")
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def get_current_user_id(payload: dict) -> int:
    """从JWT载荷中提取用户ID"""
    user_id = payload.get("userId")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token中缺少用户ID")
    return user_id


def get_current_user_role(payload: dict) -> str:
    """从JWT载荷中提取用户角色"""
    role = payload.get("role")
    if role is None:
        raise HTTPException(status_code=401, detail="Token中缺少角色信息")
    return role


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """可选认证：如果有有效Token则返回用户，否则返回None。用于公开接口的可选身份识别"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    try:
        token = auth_header[7:]
        payload = decode_jwt(token)
        username = payload.get("sub")
        if username:
            result = await db.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()
    except Exception:
        pass
    return None


def require_role(role: str):
    """角色访问控制依赖工厂——限制只有指定角色的用户才能访问。
    使用方式: `current_user: User = Depends(require_role("HR"))`"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="无权访问该资源")
        return current_user
    return role_checker


def require_any_role(*roles: str):
    """多角色访问控制依赖工厂——允许多个角色中的任一角色访问。
    使用方式: `current_user: User = Depends(require_any_role("HR", "INTERVIEWER"))`"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="无权访问该资源")
        return current_user
    return role_checker
