@echo off
echo ========================================
echo 启动短剧生产力工具服务器
echo ========================================
echo.
echo 服务器启动中...
echo.
echo 访问地址：
echo   - API文档: http://localhost:8000/api/docs
echo   - 健康检查: http://localhost:8000/health
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
