@echo off
REM Windows项目初始化脚本

echo 初始化短剧/漫剧生产力工具项目...

REM 创建虚拟环境
if not exist venv (
    echo 创建Python虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装Python依赖...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 创建.env文件
if not exist .env (
    echo 创建.env文件...
    copy .env.example .env
)

REM 创建存储目录
echo 创建存储目录...
if not exist storage mkdir storage

echo 项目初始化完成！
echo 运行 'venv\Scripts\activate.bat' 激活虚拟环境
echo 运行 'scripts\dev.bat' 启动开发服务器
pause
