"""
认证服务 - 用户登录、注册、Token签发与刷新、密码加解密
对应 Java 版本: AuthService.java + JwtTokenProvider.java
"""
from datetime import datetime, timedelta, timezone
from jose import jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, AuthResponse, UserInfo
from app.api.exception_handlers import BusinessException


def hash_password(password: str) -> str:
    """使用bcrypt对密码进行哈希加密"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与bcrypt哈希是否匹配"""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_token(data: dict, expires_delta_ms: int) -> str:
    """创建JWT令牌，包含过期时间(exp)和签发时间(iat)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(milliseconds=expires_delta_ms)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")


def generate_access_token(user: User) -> str:
    """生成访问令牌（Access Token），包含用户名、ID、角色"""
    claims = {
        "sub": user.username,
        "userId": user.id,
        "role": user.role,
    }
    return create_token(claims, settings.jwt_expiration)


def generate_refresh_token(user: User) -> str:
    """生成刷新令牌（Refresh Token），用于无感续期"""
    claims = {
        "sub": user.username,
        "userId": user.id,
        "type": "refresh",
    }
    return create_token(claims, settings.jwt_refresh_expiration)


def build_auth_response(user: User, access_token: str, refresh_token: str) -> AuthResponse:
    """构建认证响应，包含Token和用户信息"""
    return AuthResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        tokenType="Bearer",
        expiresIn=settings.jwt_expiration // 1000,
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            preferredModel=user.preferred_model,
        ),
    )


class AuthService:
    """认证服务类 - 处理用户登录、注册、Token刷新等业务逻辑"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, request: LoginRequest) -> AuthResponse:
        """用户登录：验证用户名密码 -> 签发双Token -> 返回用户信息"""
        result = await self.db.execute(select(User).where(User.username == request.username))
        user = result.scalar_one_or_none()
        if user is None:
            raise BusinessException("用户名或密码错误", 401)
        if not verify_password(request.password, user.password):
            raise BusinessException("用户名或密码错误", 401)

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        return build_auth_response(user, access_token, refresh_token)

    async def register(self, request: RegisterRequest) -> AuthResponse:
        """用户注册：校验用户名/邮箱唯一性 -> 创建用户 -> 签发Token"""
        # 检查用户名是否已存在
        result = await self.db.execute(select(User).where(User.username == request.username))
        if result.scalar_one_or_none():
            raise BusinessException("用户名已存在: " + request.username)

        # 检查邮箱是否已被使用
        if request.email:
            result = await self.db.execute(select(User).where(User.email == request.email))
            if result.scalar_one_or_none():
                raise BusinessException("邮箱已被使用: " + request.email)

        user = User(
            username=request.username,
            password=hash_password(request.password),
            email=request.email,
            role=request.role,
            preferred_model="aliyun",
        )
        self.db.add(user)
        await self.db.flush()

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        return build_auth_response(user, access_token, refresh_token)

    async def refresh_token(self, refresh_token_str: str) -> AuthResponse:
        """刷新令牌：验证refresh token -> 签发新的access和refresh token"""
        try:
            payload = jwt.decode(refresh_token_str, settings.jwt_secret, algorithms=["HS256"])
            if payload.get("type") != "refresh":
                raise BusinessException("无效的刷新令牌", 401)
            username = payload.get("sub")
            result = await self.db.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            if user is None:
                raise BusinessException("用户不存在", 401)

            access_token = generate_access_token(user)
            new_refresh_token = generate_refresh_token(user)
            return build_auth_response(user, access_token, new_refresh_token)
        except Exception as e:
            if isinstance(e, BusinessException):
                raise
            raise BusinessException("无效的刷新令牌", 401)

    @staticmethod
    def get_current_user_info(user: User) -> UserInfo:
        """获取当前登录用户的信息（脱敏）"""
        return UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            preferredModel=user.preferred_model,
        )
