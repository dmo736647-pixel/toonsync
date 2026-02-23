@echo off
REM ========================================
REM Cloudflare + Railway 部署脚本
REM ========================================

echo.
echo ========================================
echo 短剧生产力工具 - Cloudflare部署
echo ========================================
echo.

REM 检查是否安装了必要的工具
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未安装Git，请先安装Git
    pause
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未安装Node.js/npm，请先安装Node.js
    pause
    exit /b 1
)

echo [步骤 1/5] 检查环境配置...
if not exist ".env.production" (
    echo [警告] 未找到 .env.production 文件
    echo 请复制 .env.production.example 为 .env.production 并填写配置
    pause
    exit /b 1
)

echo [步骤 2/5] 构建前端...
cd frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 前端依赖安装失败
    cd ..
    pause
    exit /b 1
)

call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 前端构建失败
    cd ..
    pause
    exit /b 1
)
cd ..

echo [步骤 3/5] 提交代码到Git...
git add .
git commit -m "Deploy to production"
git push origin main

echo.
echo [步骤 4/5] 后端部署说明
echo ========================================
echo 1. 访问 https://railway.app/
echo 2. 点击 "New Project" - "Deploy from GitHub repo"
echo 3. 选择你的仓库
echo 4. 在环境变量中添加 .env.production 的内容
echo 5. Railway会自动部署
echo.
echo 部署完成后，你会得到一个URL：
echo https://你的项目.railway.app
echo ========================================
echo.

echo [步骤 5/5] 前端部署说明
echo ========================================
echo 方法1：Cloudflare Pages（推荐）
echo 1. 访问 https://dash.cloudflare.com/
echo 2. 进入 "Pages" - "Create a project"
echo 3. 连接GitHub仓库
echo 4. 配置：
echo    - Build command: cd frontend ^&^& npm run build
echo    - Build output: frontend/dist
echo 5. 添加环境变量：
echo    VITE_API_URL=https://你的项目.railway.app
echo.
echo 方法2：手动部署
echo 1. 安装Wrangler: npm install -g wrangler
echo 2. 登录: wrangler login
echo 3. 部署: cd frontend ^&^& wrangler pages publish dist
echo ========================================
echo.

echo [完成] 部署准备完成！
echo 请按照上述说明在Railway和Cloudflare上完成部署
echo.
pause
