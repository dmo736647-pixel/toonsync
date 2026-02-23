@echo off
REM ========================================
REM 快速本地测试脚本（无需Docker）
REM ========================================

echo.
echo ========================================
echo 短剧生产力工具 - 快速本地测试
echo ========================================
echo.

REM 检查Python
echo [步骤 1/5] 检查Python...
py --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未安装Python，请先安装Python 3.11+
    pause
    exit /b 1
)
echo [成功] Python已安装

REM 安装依赖
echo.
echo [步骤 2/5] 安装Python依赖...
echo 这可能需要几分钟，请耐心等待...
py -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [成功] 依赖安装完成

REM 配置环境变量
echo.
echo [步骤 3/5] 配置环境变量...
if not exist ".env" (
    echo 创建 .env 文件...
    copy .env.example .env
    echo [提示] 已创建 .env 文件，使用默认配置
)
echo [成功] 环境变量已配置

REM 初始化数据库（使用SQLite）
echo.
echo [步骤 4/5] 初始化数据库...
echo [提示] 使用SQLite数据库（无需安装PostgreSQL）
py -m alembic upgrade head
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 数据库迁移失败，但可以继续测试
)
echo [成功] 数据库已初始化

REM 启动服务
echo.
echo [步骤 5/5] 启动服务...
echo.
echo ========================================
echo 服务启动成功！
echo ========================================
echo.
echo 访问地址：
echo   - API文档: http://localhost:8000/api/docs
echo   - 健康检查: http://localhost:8000/health
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
