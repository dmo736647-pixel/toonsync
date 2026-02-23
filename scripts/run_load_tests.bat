@echo off
REM 运行负载测试脚本

echo ========================================
echo 运行负载测试
echo ========================================
echo.
echo 警告: 负载测试需要较长时间运行
echo.

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo 错误: 虚拟环境不存在，请先运行 scripts\setup.bat
    exit /b 1
)

echo 运行负载测试...
echo.

REM 运行负载测试
pytest tests/test_load_*.py -v -m load --tb=short -s

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 负载测试通过！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 负载测试失败！
    echo ========================================
    exit /b 1
)
