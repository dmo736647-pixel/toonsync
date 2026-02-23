@echo off
REM 设置Python虚拟环境和安装依赖

echo ========================================
echo 短剧生产力工具 - 环境设置
echo ========================================
echo.

REM 检查Python是否安装
py --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 检测到Python版本:
py --version
echo.

REM 创建虚拟环境
if exist venv (
    echo [2/4] 虚拟环境已存在，跳过创建
) else (
    echo [2/4] 创建虚拟环境...
    py -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)
echo.

REM 激活虚拟环境
echo [3/4] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)
echo.

REM 升级pip
echo [3.5/4] 升级pip...
python -m pip install --upgrade pip
echo.

REM 安装依赖
echo [4/4] 安装项目依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)
echo.

echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 下次使用时，请先激活虚拟环境：
echo   venv\Scripts\activate.bat
echo.
echo 然后可以运行测试：
echo   python -m pytest tests/
echo.
pause
