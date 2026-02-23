@echo off
REM 检查点7验证脚本 - 核心AI引擎验证

echo ========================================
echo 检查点7：核心AI引擎验证
echo ========================================
echo.

echo 正在运行检查点7测试...
echo.

REM 运行检查点7测试
python -m pytest tests/test_checkpoint_7.py -v --tb=short

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 检查点7验证通过！
    echo ========================================
    echo.
    echo 已验证的功能：
    echo   ✓ 中文口型同步引擎
    echo   ✓ 角色一致性引擎
    echo   ✓ 口型同步精度 ^< 50ms
    echo   ✓ 角色一致性 ^> 90%%/85%%
    echo   ✓ 性能指标满足要求
    echo   ✓ 集成工作流正常
    echo.
) else (
    echo.
    echo ========================================
    echo 检查点7验证失败！
    echo ========================================
    echo.
    echo 请检查测试输出以了解失败原因。
    echo.
    exit /b 1
)
