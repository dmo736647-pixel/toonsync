@echo off
REM 运行所有测试（单元测试、属性测试、集成测试、E2E测试）

echo ========================================
echo 运行完整测试套件
echo ========================================
echo.

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo 错误: 虚拟环境不存在，请先运行 scripts\setup.bat
    exit /b 1
)

echo.
echo [1/4] 运行单元测试...
echo ========================================
pytest tests/ -v --ignore=tests/test_integration_*.py --ignore=tests/test_e2e_*.py --ignore=tests/test_load_*.py -m "not slow" --tb=short

if %ERRORLEVEL% NEQ 0 (
    echo 单元测试失败！
    exit /b 1
)

echo.
echo [2/4] 运行集成测试...
echo ========================================
pytest tests/test_integration_*.py -v --tb=short

if %ERRORLEVEL% NEQ 0 (
    echo 集成测试失败！
    exit /b 1
)

echo.
echo [3/4] 运行端到端测试...
echo ========================================
pytest tests/test_e2e_*.py -v -m e2e --tb=short

if %ERRORLEVEL% NEQ 0 (
    echo 端到端测试失败！
    exit /b 1
)

echo.
echo [4/4] 生成测试报告...
echo ========================================
pytest tests/ --cov=app --cov-report=html --cov-report=term --ignore=tests/test_load_*.py -m "not slow"

echo.
echo ========================================
echo 所有测试通过！
echo ========================================
echo.
echo 测试覆盖率报告已生成: htmlcov/index.html
