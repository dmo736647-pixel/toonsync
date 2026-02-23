@echo off
echo ========================================
echo 启动前端界面
echo ========================================
echo.

REM 设置Node.js路径
set NODE_PATH=D:\kaifa\Node
set PATH=%NODE_PATH%;%PATH%

echo [步骤 1/3] 检查Node.js...
node --version
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Node.js未找到
    pause
    exit /b 1
)
echo [成功] Node.js已找到

echo.
echo [步骤 2/3] 安装依赖...
echo 这可能需要2-3分钟，请耐心等待...
cd frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 依赖安装可能有问题，但继续尝试启动...
)

echo.
echo [步骤 3/3] 启动开发服务器...
echo.
echo ========================================
echo 前端服务启动成功！
echo ========================================
echo.
echo 访问地址：
echo   - 前端界面: http://localhost:5173
echo   - API文档: http://localhost:8000/api/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

call npm run dev
