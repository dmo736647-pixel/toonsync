"""FastAPI应用主入口"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth, subscription, usage, project, collaboration, lip_sync, character_consistency, video_rendering, sound_effect, workflow, billing, asset_library, monitoring, websocket, onboarding, storyboard, paypal
from app.services.monitoring import monitoring_service


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="专为中文微短剧优化的一站式AI创作平台",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS配置
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:8000",
    "https://toonsync.space",
    "https://www.toonsync.space",
    "https://api.toonsync.space",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 监控中间件
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    """监控中间件：记录请求指标"""
    start_time = time.time()
    
    # 增加请求计数
    api_requests = monitoring_service.get_metric("api_requests_total")
    if api_requests:
        api_requests.inc(labels={"method": request.method, "path": request.url.path})
    
    try:
        response = await call_next(request)
        
        # 记录响应时间
        duration = time.time() - start_time
        api_response_time = monitoring_service.get_metric("api_response_time_seconds")
        if api_response_time:
            api_response_time.observe(duration, labels={"method": request.method, "path": request.url.path})
        
        return response
    except Exception as e:
        # 增加错误计数
        api_errors = monitoring_service.get_metric("api_errors_total")
        if api_errors:
            api_errors.inc(labels={"method": request.method, "path": request.url.path, "error": type(e).__name__})
        raise


# 注册路由
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(subscription.router, prefix=settings.API_V1_PREFIX)
app.include_router(usage.router, prefix=settings.API_V1_PREFIX)
app.include_router(billing.router, prefix=settings.API_V1_PREFIX)
app.include_router(project.router, prefix=settings.API_V1_PREFIX)
app.include_router(collaboration.router, prefix=settings.API_V1_PREFIX)
app.include_router(lip_sync.router, prefix=settings.API_V1_PREFIX)
app.include_router(character_consistency.router, prefix=settings.API_V1_PREFIX)
app.include_router(video_rendering.router, prefix=settings.API_V1_PREFIX)
app.include_router(sound_effect.router, prefix=settings.API_V1_PREFIX)
app.include_router(workflow.router, prefix=settings.API_V1_PREFIX)
app.include_router(asset_library.router, prefix=settings.API_V1_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket.router, prefix=settings.API_V1_PREFIX)
app.include_router(onboarding.router, prefix=settings.API_V1_PREFIX)
app.include_router(storyboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(paypal.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    """健康检查端点"""
    return {"status": "ok", "message": "短剧/漫剧生产力工具API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查端点"""
    return {"status": "healthy"}
