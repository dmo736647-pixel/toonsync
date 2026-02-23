@echo off
REM 导入音效库数据脚本

echo ========================================
echo 导入音效库数据
echo ========================================
echo.

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 运行导入脚本
python scripts\import_sound_effects.py

echo.
echo ========================================
echo 导入完成
echo ========================================

pause
