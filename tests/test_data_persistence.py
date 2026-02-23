"""数据持久化功能测试"""
import pytest
from sqlalchemy import text
from app.core.database import get_db, engine
from app.core.cache import cache_manager
from app.core.storage import storage_manager
from io import BytesIO


class TestDatabasePersistence:
    """测试数据库持久化"""
    
    def test_database_connection(self):
        """测试数据库连接"""
        db = next(get_db())
        try:
            # 执行简单查询验证连接
            result = db.execute(text("SELECT 1"))
            assert result.scalar() == 1
        finally:
            db.close()
    
    def test_database_transaction(self):
        """测试数据库事务"""
        db = next(get_db())
        try:
            # 开始事务
            db.begin()
            
            # 执行操作
            db.execute(text("SELECT 1"))
            
            # 提交事务
            db.commit()
            
            assert True
        except Exception as e:
            db.rollback()
            pytest.fail(f"数据库事务失败: {str(e)}")
        finally:
            db.close()


class TestCachePersistence:
    """测试缓存持久化"""
    
    @pytest.mark.asyncio
    async def test_cache_connection(self):
        """测试Redis连接"""
        await cache_manager.connect()
        try:
            # 测试设置和获取
            key = "test_key"
            value = "test_value"
            
            success = await cache_manager.set(key, value)
            assert success, "缓存设置失败"
            
            cached_value = await cache_manager.get(key)
            assert cached_value == value, "缓存获取失败"
            
            # 清理
            await cache_manager.delete(key)
        finally:
            await cache_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """测试缓存过期"""
        await cache_manager.connect()
        try:
            key = "test_expire_key"
            value = "test_value"
            
            # 设置1秒过期
            await cache_manager.set(key, value, expire=1)
            
            # 立即获取应该存在
            cached_value = await cache_manager.get(key)
            assert cached_value == value
            
            # 等待2秒后应该过期
            import asyncio
            await asyncio.sleep(2)
            
            cached_value = await cache_manager.get(key)
            assert cached_value is None, "缓存应该已过期"
        finally:
            await cache_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_cache_json_data(self):
        """测试缓存JSON数据"""
        await cache_manager.connect()
        try:
            key = "test_json_key"
            value = {"name": "test", "count": 123, "items": [1, 2, 3]}
            
            await cache_manager.set(key, value)
            cached_value = await cache_manager.get(key)
            
            assert cached_value == value
            assert isinstance(cached_value, dict)
            
            # 清理
            await cache_manager.delete(key)
        finally:
            await cache_manager.disconnect()


class TestStoragePersistence:
    """测试对象存储持久化"""
    
    def test_storage_upload_and_download(self):
        """测试文件上传和下载"""
        # 创建测试文件
        test_content = b"This is a test file content"
        test_file = BytesIO(test_content)
        object_key = "test/test_file.txt"
        
        try:
            # 上传文件
            url = storage_manager.upload_file(test_file, object_key)
            assert url is not None, "文件上传失败"
            
            # 验证文件存在
            exists = storage_manager.file_exists(object_key)
            assert exists, "上传的文件不存在"
            
            # 下载文件
            downloaded_content = storage_manager.download_file(object_key)
            assert downloaded_content == test_content, "下载的内容不匹配"
        
        finally:
            # 清理测试文件
            storage_manager.delete_file(object_key)
    
    def test_storage_delete(self):
        """测试文件删除"""
        # 创建测试文件
        test_content = b"Test delete"
        test_file = BytesIO(test_content)
        object_key = "test/delete_test.txt"
        
        # 上传文件
        storage_manager.upload_file(test_file, object_key)
        
        # 验证文件存在
        assert storage_manager.file_exists(object_key)
        
        # 删除文件
        success = storage_manager.delete_file(object_key)
        assert success, "文件删除失败"
        
        # 验证文件不存在
        assert not storage_manager.file_exists(object_key)
    
    def test_storage_file_not_found(self):
        """测试下载不存在的文件"""
        object_key = "test/nonexistent_file.txt"
        
        with pytest.raises((FileNotFoundError, Exception)):
            storage_manager.download_file(object_key)
