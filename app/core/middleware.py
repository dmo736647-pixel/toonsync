"""中间件"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from typing import Callable

from app.services.isolation import rate_limiter, error_isolation, resource_limiter


async def rate_limit_middleware(request: Request, call_next: Callable):
    """
    速率限制中间件
    
    限制每个用户的请求频率，防止滥用
    """
    # 获取用户ID（从认证token中）
    user_id = request.state.user_id if hasattr(request.state, "user_id") else "anonymous"
    
    # 确定限制类型
    limit_type = "default"
    if "/api/upload" in request.url.path:
        limit_type = "upload"
    elif "/api/export" in request.url.path:
        limit_type = "export"
    elif request.url.path.startswith("/api/"):
        limit_type = "api"
    
    # 检查速率限制
    allowed, wait_time = rate_limiter.check_rate_limit(user_id, limit_type)
    
    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"请求过于频繁，请在{wait_time}秒后重试",
                    "retry_after": wait_time
                }
            },
            headers={"Retry-After": str(wait_time)}
        )
    
    # 继续处理请求
    response = await call_next(request)
    
    # 添加速率限制信息到响应头
    remaining = rate_limiter.get_remaining_quota(user_id, limit_type)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response


async def error_isolation_middleware(request: Request, call_next: Callable):
    """
    错误隔离中间件
    
    隔离频繁出错的用户，防止影响其他用户
    """
    # 获取用户ID
    user_id = request.state.user_id if hasattr(request.state, "user_id") else "anonymous"
    
    # 检查是否应该隔离
    if error_isolation.should_isolate(user_id):
        error_count = error_isolation.get_error_count(user_id)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "USER_ISOLATED",
                    "message": f"由于频繁错误（{error_count}次），您的账户已被临时限制，请稍后重试",
                    "suggestion": "请检查您的操作是否正确，或联系技术支持"
                }
            }
        )
    
    try:
        # 处理请求
        response = await call_next(request)
        return response
    
    except Exception as e:
        # 记录错误
        error_isolation.record_error(user_id, e)
        
        # 重新抛出异常，让全局错误处理器处理
        raise


async def resource_limit_middleware(request: Request, call_next: Callable):
    """
    资源限制中间件
    
    限制每个用户的资源使用，防止资源耗尽
    """
    # 获取用户ID
    user_id = request.state.user_id if hasattr(request.state, "user_id") else "anonymous"
    
    # 检查请求数限制
    if not resource_limiter.check_resource_limit(user_id, "requests", 1):
        usage = resource_limiter.get_resource_usage(user_id)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "RESOURCE_LIMIT_EXCEEDED",
                    "message": "您已达到资源使用限制",
                    "usage": usage,
                    "suggestion": "请等待资源配额重置或升级订阅计划"
                }
            }
        )
    
    # 记录请求开始时间
    start_time = time.time()
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 记录CPU时间
        cpu_time = time.time() - start_time
        resource_limiter.check_resource_limit(user_id, "cpu_time", cpu_time)
        
        # 添加资源使用信息到响应头
        usage = resource_limiter.get_resource_usage(user_id)
        response.headers["X-Resource-Usage"] = str(usage["requests"])
        response.headers["X-Resource-Limit"] = str(usage["limits"]["requests"])
        
        return response
    
    except Exception as e:
        # 即使出错也记录CPU时间
        cpu_time = time.time() - start_time
        resource_limiter.check_resource_limit(user_id, "cpu_time", cpu_time)
        raise


async def user_context_middleware(request: Request, call_next: Callable):
    """
    用户上下文中间件
    
    从认证token中提取用户信息并设置到请求上下文
    """
    from app.services.auth import AuthenticationService
    from app.core.database import get_db
    
    # 从Authorization头获取token
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
        try:
            # 验证JWT token
            db = next(get_db())
            auth_service = AuthenticationService(db)
            user = auth_service.get_current_user(token)
            
            if user:
                request.state.user_id = str(user.id)
                request.state.user = user
            else:
                request.state.user_id = "anonymous"
        except Exception:
            request.state.user_id = "anonymous"
    else:
        request.state.user_id = "anonymous"
    
    response = await call_next(request)
    return response
