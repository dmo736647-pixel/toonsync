@echo off
REM 运行端到端测试脚本

echo ========================================
echo 运行端到端测试
echo ========================================
echo.

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo 错误: 虚拟环境不存在，请先运行 scripts\setup.bat
    exit /b 1
)

echo 运行端到端测试...
echo.

REM 运行E2E测试
pytest tests/test_e2e_*.py -v -m e2e --tb=short

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 端到端测试通过！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 端到端测试失败！
    echo ========================================
    exit /b 1
)
