@echo off
chcp 65001 >nul
title AI Manju Maker Launcher

echo ========================================
echo AI漫剧制作器 - 一键启动脚本
echo ========================================
echo.

echo [1/3] 正在启动后端服务 (端口 8000)...
start "Backend Server" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [2/3] 正在启动前端服务 (端口 5173)...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo [3/3] 服务启动中...
echo.
echo 请等待两个新窗口出现并完成启动。
echo.
echo 后端API地址: http://localhost:8000/docs
echo 前端访问地址: http://localhost:5173
echo.
echo ========================================
echo 注意事项：
echo 1. 请确保已在 .env 文件中配置 REPLICATE_API_TOKEN
echo 2. 如果前端启动失败，请先运行 cd frontend && npm install
echo ========================================
pause
