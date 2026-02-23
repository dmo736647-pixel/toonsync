@echo off
REM 检查点11验证脚本 - 工作流集成验证

echo ========================================
echo 检查点11：工作流集成验证
echo ========================================
echo.

echo [1/3] 运行工作流集成测试...
pytest tests/test_checkpoint_11.py -v --tb=short

echo.
echo [2/3] 运行所有单元测试...
pytest tests/ -k "not properties" --tb=short -q

echo.
echo [3/3] 运行所有属性测试...
pytest tests/ -k "properties" --tb=short -q

echo.
echo ========================================
echo 检查点11验证完成
echo ========================================
