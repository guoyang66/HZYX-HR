"""
认证相关数据传输对象（DTO）- 登录/注册请求和响应模型
"""
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class RegisterRequest(BaseModel):
    """注册请求 - 包含Role字段决定用户类型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    email: str | None = None
    role: str = Field(..., pattern=r"^(HR|INTERVIEWER)$", description="角色")


class UserInfo(BaseModel):
    """用户信息（脱敏，不含密码）"""
    id: int
    username: str
    email: str | None = None
    role: str
    preferred_model: str = "aliyun"  # 用户首选AI模型


class AuthResponse(BaseModel):
    """认证响应 - 包含双Token和用户信息"""
    accessToken: str        # 访问令牌（24小时有效）
    refreshToken: str       # 刷新令牌（7天有效）
    tokenType: str = "Bearer"
    expiresIn: int          # accessToken过期时间（秒）
    user: UserInfo
