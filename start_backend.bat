@echo off
chcp 65001 >nul
title Backend API Server
cd /d D:\ceshi\manju

echo ========================================
echo Starting Backend Server...
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR: Server failed to start!
    echo ========================================
)

echo.
echo ========================================
echo Press any key to close...
echo ========================================
pause
