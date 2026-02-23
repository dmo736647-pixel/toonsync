"""数据备份和恢复服务"""
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import gzip
import shutil

from app.core.config import settings
from app.core.storage import storage_manager


class BackupService:
    """数据备份和恢复服务"""
    
    def __init__(self):
        self.backup_dir = Path("./backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = 90  # 保留90天
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        创建数据库备份
        
        参数:
            backup_name: 备份名称，如果为None则使用时间戳
        
        返回:
            备份文件路径
        
        需求：11.2
        """
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_file = self.backup_dir / f"{backup_name}.sql"
        compressed_file = self.backup_dir / f"{backup_name}.sql.gz"
        
        try:
            # 使用pg_dump创建备份
            dump_command = [
                "pg_dump",
                "-h", settings.POSTGRES_HOST,
                "-p", str(settings.POSTGRES_PORT),
                "-U", settings.POSTGRES_USER,
                "-d", settings.POSTGRES_DB,
                "-f", str(backup_file),
                "--no-password"
            ]
            
            # 设置环境变量以避免密码提示
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
            
            # 执行备份
            result = subprocess.run(
                dump_command,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"备份失败: {result.stderr}")
            
            # 压缩备份文件
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除未压缩的文件
            backup_file.unlink()
            
            # 上传到云存储
            with open(compressed_file, 'rb') as f:
                storage_key = f"backups/{backup_name}.sql.gz"
                storage_manager.upload_file(f, storage_key)
            
            return str(compressed_file)
        
        except Exception as e:
            # 清理失败的备份文件
            if backup_file.exists():
                backup_file.unlink()
            if compressed_file.exists():
                compressed_file.unlink()
            raise Exception(f"创建备份失败: {str(e)}")
    
    def restore_backup(self, backup_file: str) -> bool:
        """
        从备份恢复数据库
        
        参数:
            backup_file: 备份文件路径
        
        返回:
            是否恢复成功
        
        需求：11.3
        """
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        # 解压备份文件
        sql_file = backup_path.with_suffix('')
        
        try:
            with gzip.open(backup_path, 'rb') as f_in:
                with open(sql_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 使用psql恢复数据库
            restore_command = [
                "psql",
                "-h", settings.POSTGRES_HOST,
                "-p", str(settings.POSTGRES_PORT),
                "-U", settings.POSTGRES_USER,
                "-d", settings.POSTGRES_DB,
                "-f", str(sql_file),
                "--no-password"
            ]
            
            # 设置环境变量
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
            
            # 执行恢复
            result = subprocess.run(
                restore_command,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"恢复失败: {result.stderr}")
            
            return True
        
        except Exception as e:
            raise Exception(f"恢复备份失败: {str(e)}")
        
        finally:
            # 清理解压的SQL文件
            if sql_file.exists():
                sql_file.unlink()
    
    def list_backups(self) -> List[dict]:
        """
        列出所有备份
        
        返回:
            备份列表，每个备份包含名称、大小、创建时间
        """
        backups = []
        
        for backup_file in self.backup_dir.glob("*.sql.gz"):
            stat = backup_file.stat()
            backups.append({
                "name": backup_file.stem,
                "file": str(backup_file),
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime)
            })
        
        # 按创建时间倒序排序
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self) -> int:
        """
        清理超过保留期的备份
        
        返回:
            删除的备份数量
        
        需求：11.4
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("*.sql.gz"):
            stat = backup_file.stat()
            created_at = datetime.fromtimestamp(stat.st_mtime)
            
            if created_at < cutoff_date:
                # 从本地删除
                backup_file.unlink()
                
                # 从云存储删除
                storage_key = f"backups/{backup_file.name}"
                storage_manager.delete_file(storage_key)
                
                deleted_count += 1
        
        return deleted_count
    
    def get_latest_backup(self) -> Optional[str]:
        """
        获取最新的备份文件
        
        返回:
            最新备份文件路径，如果没有备份则返回None
        """
        backups = self.list_backups()
        
        if backups:
            return backups[0]["file"]
        
        return None
    
    def schedule_automatic_backup(self) -> None:
        """
        调度自动备份（每24小时）
        
        注意：这是一个简化的实现，生产环境应使用cron或类似的调度工具
        
        需求：11.2
        """
        # 创建备份
        self.create_backup()
        
        # 清理旧备份
        self.cleanup_old_backups()


# 全局备份服务实例
backup_service = BackupService()
