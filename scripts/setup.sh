#!/bin/bash

# 项目初始化脚本

echo "初始化短剧/漫剧生产力工具项目..."

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建.env文件
if [ ! -f .env ]; then
    echo "创建.env文件..."
    cp .env.example .env
fi

# 创建存储目录
echo "创建存储目录..."
mkdir -p storage

echo "项目初始化完成！"
echo "运行 'source venv/bin/activate' 激活虚拟环境"
echo "运行 'bash scripts/dev.sh' 启动开发服务器"
