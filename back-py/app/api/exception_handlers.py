"""
全局异常处理 - 统一拦截各类异常并返回标准 ApiResponse 格式
对应 Java 版本: @RestControllerAdvice + GlobalExceptionHandler
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.common import ApiResponse


class BusinessException(Exception):
    """业务异常类 - 可携带状态码（默认400）"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理器 - 返回对应状态码和错误信息"""
    return JSONResponse(
        status_code=exc.code if exc.code < 500 else 400,
        content=ApiResponse.error(exc.code, exc.message).model_dump(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求参数校验异常处理器 - 返回400"""
    return JSONResponse(
        status_code=400,
        content=ApiResponse.bad_request("参数校验失败").model_dump(),
    )


async def http_exception_handler(request: Request, exc):
    """HTTP异常处理器 - 统一处理401/403/404"""
    from fastapi import HTTPException as FastAPIHTTPException
    if isinstance(exc, FastAPIHTTPException):
        code_map = {401: 401, 403: 403, 404: 404}
        code = code_map.get(exc.status_code, 500)
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse.error(code, exc.detail).model_dump(),
        )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器 - 兜底捕获所有未处理的异常，返回500"""
    return JSONResponse(
        status_code=500,
        content=ApiResponse.error(500, f"服务器内部错误: {str(exc)}").model_dump(),
    )


def register_exception_handlers(app):
    """向FastAPI应用注册所有异常处理器"""
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
