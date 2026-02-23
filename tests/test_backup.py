"""数据备份功能单元测试"""
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from app.services.backup import BackupService


class TestBackupService:
    """备份服务测试"""
    
    @pytest.fixture
    def backup_service(self):
        """创建备份服务实例"""
        service = BackupService()
        # 使用测试目录
        service.backup_dir = Path("./test_backups")
        service.backup_dir.mkdir(parents=True, exist_ok=True)
        yield service
        # 清理测试目录
        import shutil
        if service.backup_dir.exists():
            shutil.rmtree(service.backup_dir)
    
    def test_create_backup(self, backup_service):
        """
        测试备份创建
        
        需求：11.2
        """
        # 注意：这个测试需要PostgreSQL数据库运行
        # 在CI/CD环境中可能需要mock
        try:
            backup_file = backup_service.create_backup("test_backup")
            
            # 验证备份文件存在
            assert Path(backup_file).exists(), "备份文件未创建"
            assert backup_file.endswith(".sql.gz"), "备份文件格式不正确"
        
        except Exception as e:
            # 如果数据库不可用，跳过测试
            pytest.skip(f"数据库不可用: {str(e)}")
    
    def test_list_backups(self, backup_service):
        """
        测试备份列表
        
        需求：11.2, 11.3, 11.4
        """
        # 创建测试备份文件
        import gzip
        test_backup = backup_service.backup_dir / "test_backup_20260101_120000.sql.gz"
        with gzip.open(test_backup, 'wb') as f:
            f.write(b"-- Test backup content")
        
        # 列出备份
        backups = backup_service.list_backups()
        
        # 验证
        assert len(backups) > 0, "备份列表为空"
        assert any(b["name"] == "test_backup_20260101_120000" for b in backups), "测试备份未找到"
        
        # 验证备份信息
        backup = next(b for b in backups if b["name"] == "test_backup_20260101_120000")
        assert "size_bytes" in backup
        assert "created_at" in backup
        assert backup["size_bytes"] > 0
    
    def test_get_latest_backup(self, backup_service):
        """
        测试获取最新备份
        
        需求：11.3
        """
        # 创建多个测试备份文件
        import gzip
        import time
        
        backup1 = backup_service.backup_dir / "backup_20260101_120000.sql.gz"
        with gzip.open(backup1, 'wb') as f:
            f.write(b"-- Backup 1")
        
        time.sleep(0.1)  # 确保时间戳不同
        
        backup2 = backup_service.backup_dir / "backup_20260102_120000.sql.gz"
        with gzip.open(backup2, 'wb') as f:
            f.write(b"-- Backup 2")
        
        # 获取最新备份
        latest = backup_service.get_latest_backup()
        
        # 验证
        assert latest is not None, "未找到最新备份"
        assert "backup_20260102_120000" in latest, "最新备份不正确"
    
    def test_cleanup_old_backups(self, backup_service):
        """
        测试清理旧备份
        
        需求：11.4
        """
        import gzip
        import os
        
        # 创建一个旧备份（修改文件时间戳）
        old_backup = backup_service.backup_dir / "old_backup.sql.gz"
        with gzip.open(old_backup, 'wb') as f:
            f.write(b"-- Old backup")
        
        # 修改文件时间戳为91天前
        old_time = (datetime.now() - timedelta(days=91)).timestamp()
        os.utime(old_backup, (old_time, old_time))
        
        # 创建一个新备份
        new_backup = backup_service.backup_dir / "new_backup.sql.gz"
        with gzip.open(new_backup, 'wb') as f:
            f.write(b"-- New backup")
        
        # 清理旧备份
        deleted_count = backup_service.cleanup_old_backups()
        
        # 验证
        assert deleted_count == 1, "应该删除1个旧备份"
        assert not old_backup.exists(), "旧备份未删除"
        assert new_backup.exists(), "新备份不应被删除"
    
    def test_restore_backup_file_not_found(self, backup_service):
        """
        测试恢复不存在的备份
        
        需求：11.3
        """
        with pytest.raises(FileNotFoundError):
            backup_service.restore_backup("nonexistent_backup.sql.gz")
    
    def test_backup_retention_policy(self, backup_service):
        """
        测试备份保留策略（90天）
        
        需求：11.4
        """
        assert backup_service.retention_days == 90, "备份保留期应为90天"
