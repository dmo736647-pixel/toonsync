"""自动备份调度脚本

这个脚本应该通过cron或Windows任务计划程序每24小时运行一次

Linux cron示例:
0 2 * * * /usr/bin/python /path/to/scripts/schedule_backup.py

Windows任务计划程序:
创建一个每天凌晨2点运行的任务
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.backup import backup_service
from datetime import datetime


def main():
    """执行自动备份"""
    print(f"[{datetime.now()}] 开始自动备份...")
    
    try:
        # 创建备份
        backup_file = backup_service.create_backup()
        print(f"[{datetime.now()}] 备份创建成功: {backup_file}")
        
        # 清理旧备份
        deleted_count = backup_service.cleanup_old_backups()
        print(f"[{datetime.now()}] 已清理{deleted_count}个过期备份")
        
        print(f"[{datetime.now()}] 自动备份完成")
        return 0
    
    except Exception as e:
        print(f"[{datetime.now()}] 自动备份失败: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
