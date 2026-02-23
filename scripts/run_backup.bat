@echo off
REM 运行数据库备份脚本

echo 开始数据库备份...
python scripts\schedule_backup.py

if %ERRORLEVEL% EQU 0 (
    echo 备份成功完成
) else (
    echo 备份失败
    exit /b 1
)
