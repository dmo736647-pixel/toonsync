@echo off
REM 检查点4验证脚本 - Windows版本

echo ========================================
echo 检查点4：认证和项目管理功能验证
echo ========================================
echo.

REM 检查虚拟环境
if not exist venv (
    echo [错误] 虚拟环境不存在！
    echo 请先运行 scripts\setup.bat 创建虚拟环境
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/5] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 运行检查点4集成测试
echo.
echo [2/5] 运行检查点4集成测试...
echo ----------------------------------------
python -m pytest tests/test_checkpoint_4.py -v --tb=short
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [警告] 检查点4集成测试失败！
    echo 请检查测试输出以了解详情。
)

REM 运行认证相关测试
echo.
echo [3/5] 运行认证功能测试...
echo ----------------------------------------
python -m pytest tests/test_auth.py tests/test_auth_properties.py -v --tb=short
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 认证测试失败！
)

REM 运行订阅和额度测试
echo.
echo [4/5] 运行订阅和额度管理测试...
echo ----------------------------------------
python -m pytest tests/test_subscription.py tests/test_subscription_properties.py tests/test_usage_properties.py -v --tb=short
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 订阅/额度测试失败！
)

REM 运行项目管理测试
echo.
echo [5/5] 运行项目管理和协作测试...
echo ----------------------------------------
python -m pytest tests/test_project.py tests/test_project_properties.py tests/test_collaboration.py tests/test_collaboration_properties.py tests/test_version_properties.py -v --tb=short
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 项目管理测试失败！
)

echo.
echo ========================================
echo 检查点4验证完成！
echo ========================================
echo.
echo 如果所有测试都通过，系统已准备好进入下一阶段。
echo 如果有测试失败，请查看上面的错误信息。
echo.

pause
