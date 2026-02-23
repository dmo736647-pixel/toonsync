@echo off
REM 运行计费管理测试

echo ========================================
echo 短剧生产力工具 - 计费管理测试
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist venv (
    echo [错误] 虚拟环境不存在
    echo 请先运行: scripts\setup_env.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 运行计费管理测试
echo 运行计费管理单元测试...
python -m pytest tests/test_billing.py -v --tb=short
echo.

echo 运行计费管理属性测试...
python -m pytest tests/test_billing_properties.py -v --tb=short

echo.
echo ========================================
echo 测试完成
echo ========================================
pause
