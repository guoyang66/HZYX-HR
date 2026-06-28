"""
通用响应模型 - 统一API响应格式（ApiResponse）和分页响应格式（PageResponse）
所有接口返回数据都通过此类包装，确保前后端数据格式统一
"""
from datetime import datetime, timezone
from typing import TypeVar, Generic
from pydantic import BaseModel, Field, field_serializer

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应模型，包含状态码、消息、数据和时间戳"""
    code: int = 200
    message: str = "success"
    data: T | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @field_serializer("timestamp")
    def serialize_timestamp(self, v: str) -> str:
        return v

    @classmethod
    def success(cls, data: T, message: str = "success") -> "ApiResponse[T]":
        """返回成功响应（200）"""
        return cls(code=200, message=message, data=data)

    @classmethod
    def success_message(cls, message: str) -> "ApiResponse[None]":
        """返回成功消息（200，无数据）"""
        return cls(code=200, message=message, data=None)

    @classmethod
    def error(cls, code: int, message: str) -> "ApiResponse[None]":
        """返回错误响应"""
        return cls(code=code, message=message, data=None)

    @classmethod
    def bad_request(cls, message: str = "参数校验失败") -> "ApiResponse[None]":
        """返回400错误"""
        return cls(code=400, message=message, data=None)

    @classmethod
    def unauthorized(cls, message: str = "未登录或 Token 已失效") -> "ApiResponse[None]":
        """返回401错误"""
        return cls(code=401, message=message, data=None)

    @classmethod
    def forbidden(cls, message: str = "无权访问该资源") -> "ApiResponse[None]":
        """返回403错误"""
        return cls(code=403, message=message, data=None)

    @classmethod
    def not_found(cls, message: str = "资源不存在") -> "ApiResponse[None]":
        """返回404错误"""
        return cls(code=404, message=message, data=None)


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型 - Spring Data Page风格"""
    content: list[T]       # 当前页数据
    totalElements: int     # 总记录数
    totalPages: int        # 总页数
    number: int            # 当前页码（从0开始）
    size: int              # 每页大小
