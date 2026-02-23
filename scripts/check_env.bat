@echo off
REM 检查Python环境

echo ========================================
echo Python环境诊断
echo ========================================
echo.

echo [1] 检查Python安装...
py --version
if errorlevel 1 (
    echo [X] Python未安装或不在PATH中
) else (
    echo [√] Python已安装
)
echo.

echo [2] 检查pip...
py -m pip --version
if errorlevel 1 (
    echo [X] pip未安装
) else (
    echo [√] pip已安装
)
echo.

echo [3] 检查虚拟环境...
if exist venv (
    echo [√] 虚拟环境已创建
    if exist venv\Scripts\activate.bat (
        echo [√] 激活脚本存在
    ) else (
        echo [X] 激活脚本不存在
    )
) else (
    echo [X] 虚拟环境未创建
    echo.
    echo 建议运行: scripts\setup_env.bat
)
echo.

echo [4] 检查pytest（如果虚拟环境已激活）...
if exist venv (
    call venv\Scripts\activate.bat
    python -m pytest --version 2>nul
    if errorlevel 1 (
        echo [X] pytest未安装
        echo.
        echo 建议运行: scripts\setup_env.bat
    ) else (
        echo [√] pytest已安装
    )
)
echo.

echo ========================================
echo 诊断完成
echo ========================================
echo.
echo 如果环境未设置，请运行:
echo   scripts\setup_env.bat
echo.
pause
