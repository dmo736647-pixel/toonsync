@echo off
REM Windows开发环境启动脚本

echo 启动短剧/漫剧生产力工具开发环境...

REM 检查.env文件
if not exist .env (
    echo 创建.env文件...
    copy .env.example .env
)

REM 启动Docker Compose服务
echo 启动Docker服务...
docker-compose up -d postgres redis

REM 等待数据库就绪
echo 等待数据库就绪...
timeout /t 5 /nobreak

REM 运行数据库迁移
echo 运行数据库迁移...
alembic upgrade head

REM 启动FastAPI应用
echo 启动FastAPI应用...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo 开发环境已启动！
echo API文档: http://localhost:8000/api/docs
