@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   ToonSync Quick Deploy Tool
echo ========================================
echo.

echo [1/6] Checking required tools...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git not installed
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not installed
    pause
    exit /b 1
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not installed
    pause
    exit /b 1
)

echo [OK] All required tools installed
echo.

echo [2/6] Checking environment files...
if not exist .env.production (
    echo [WARN] .env.production not found
    echo Creating from template...
    copy .env.production.example .env.production
    echo.
    echo Please edit .env.production with your config:
    echo    - DATABASE_URL
    echo    - REDIS_URL
    echo    - SECRET_KEY
    echo    - PAYPAL_CLIENT_ID
    echo    - PAYPAL_CLIENT_SECRET
    echo    - REPLICATE_API_TOKEN
    echo    - ELEVENLABS_API_KEY
    echo    - AZURE_SPEECH_KEY
    echo.
    echo Press any key after editing...
    pause >nul
) else (
    echo [OK] .env.production found
)
echo.

echo [3/6] Installing backend dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Backend dependencies install failed
    pause
    exit /b 1
)
echo [OK] Backend dependencies installed
echo.

echo [4/6] Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Frontend dependencies install failed
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Frontend dependencies installed
echo.

echo [5/6] Running database migrations...
alembic upgrade head
if %errorlevel% neq 0 (
    echo [ERROR] Database migration failed
    echo Make sure DATABASE_URL is correct
    pause
    exit /b 1
)
echo [OK] Database migrations complete
echo.

echo [6/6] Building frontend...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Frontend build complete
echo.

echo.
echo ========================================
echo   Preparation Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Deploy backend to Railway:
echo    - Visit https://railway.app/
echo    - Connect GitHub repo
echo    - Configure environment variables
echo.
echo 2. Deploy frontend to Cloudflare Pages:
echo    - Visit https://dash.cloudflare.com/
echo    - Create Pages project
echo    - Connect GitHub repo
echo.
echo 3. Configure DNS:
echo    - Add api.toonsync.space CNAME
echo    - Add www.toonsync.space CNAME
echo.
echo 4. Configure PayPal:
echo    - Create PayPal app
echo    - Get Client ID and Secret
echo.
echo See: docs/DEPLOYMENT_GUIDE_SIMPLE.md
echo.
pause
