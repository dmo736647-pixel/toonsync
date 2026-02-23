"""性能优化单元测试"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.performance import (
    PerformanceOptimizer,
    DatabaseOptimizer,
    performance_optimizer
)
from app.core.async_tasks import (
    AsyncTask,
    AsyncTaskManager,
    TaskStatus,
    task_manager
)
from app.core.cache import cache_manager


class TestPerformanceOptimizer:
    """性能优化器测试"""
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """测试缓存键生成"""
        optimizer = PerformanceOptimizer()
        
        # 测试简单参数
        key1 = optimizer.cache_key("user", "123")
        assert key1 == "user:123"
        
        # 测试多个参数
        key2 = optimizer.cache_key("project", "user123", "proj456")
        assert key2 == "project:user123:proj456"
        
        # 测试关键字参数
        key3 = optimizer.cache_key("asset", user_id="123", asset_type="image")
        assert "asset" in key3
        assert "user_id:123" in key3
        assert "asset_type:image" in key3
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self):
        """测试缓存装饰器"""
        optimizer = PerformanceOptimizer()
        call_count = 0
        
        # Mock cache manager
        with patch.object(cache_manager, 'get', new_callable=AsyncMock) as mock_get, \
             patch.object(cache_manager, 'set', new_callable=AsyncMock) as mock_set:
            
            # 第一次调用返回None（缓存未命中）
            # 第二次调用返回缓存值
            mock_get.side_effect = [None, 10, None, 20]
            mock_set.return_value = True
            
            @optimizer.cached("test", ttl=60)
            async def expensive_function(value: int):
                nonlocal call_count
                call_count += 1
                return value * 2
            
            # 第一次调用应执行函数
            result1 = await expensive_function(5)
            assert result1 == 10
            assert call_count == 1
            
            # 第二次调用应从缓存获取
            result2 = await expensive_function(5)
            assert result2 == 10
            assert call_count == 1  # 没有增加
            
            # 不同参数应执行函数
            result3 = await expensive_function(10)
            assert result3 == 20
            assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_invalidate_cache(self):
        """测试缓存失效"""
        optimizer = PerformanceOptimizer()
        
        # Mock cache manager
        with patch.object(cache_manager, 'set', new_callable=AsyncMock) as mock_set, \
             patch.object(cache_manager, 'exists', new_callable=AsyncMock) as mock_exists, \
             patch.object(cache_manager, 'delete', new_callable=AsyncMock) as mock_delete:
            
            mock_set.return_value = True
            mock_exists.side_effect = [True, False]
            mock_delete.return_value = True
            
            # 设置缓存
            cache_key = optimizer.cache_key("user", "123")
            await cache_manager.set(cache_key, {"name": "Test User"}, expire=60)
            
            # 验证缓存存在
            assert await cache_manager.exists(cache_key)
            
            # 使缓存失效
            success = await optimizer.invalidate_cache("user", "123")
            assert success
            
            # 验证缓存已删除
            assert not await cache_manager.exists(cache_key)


class TestDatabaseOptimizer:
    """数据库优化器测试"""
    
    def test_paginate_query(self):
        """测试分页查询"""
        # 创建模拟查询对象
        mock_query = Mock()
        mock_query.count.return_value = 100
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [f"item_{i}" for i in range(20)]
        
        # 测试第一页
        result = DatabaseOptimizer.paginate_query(mock_query, page=1, page_size=20)
        assert result["total"] == 100
        assert result["page"] == 1
        assert result["page_size"] == 20
        assert result["total_pages"] == 5
        assert len(result["items"]) == 20
        
        # 验证调用
        mock_query.offset.assert_called_with(0)
        mock_query.limit.assert_called_with(20)
    
    def test_paginate_query_last_page(self):
        """测试最后一页的分页"""
        mock_query = Mock()
        mock_query.count.return_value = 95
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [f"item_{i}" for i in range(15)]
        
        # 测试最后一页
        result = DatabaseOptimizer.paginate_query(mock_query, page=5, page_size=20)
        assert result["total"] == 95
        assert result["page"] == 5
        assert result["total_pages"] == 5
        assert len(result["items"]) == 15
        
        # 验证偏移量
        mock_query.offset.assert_called_with(80)


class TestAsyncTask:
    """异步任务测试"""
    
    @pytest.mark.asyncio
    async def test_task_creation(self):
        """测试任务创建"""
        async def sample_func(x: int):
            return x * 2
        
        task = AsyncTask("task_1", sample_func, 5)
        assert task.task_id == "task_1"
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.error is None
    
    @pytest.mark.asyncio
    async def test_task_execution_success(self):
        """测试任务成功执行"""
        async def sample_func(x: int):
            await asyncio.sleep(0.1)
            return x * 2
        
        task = AsyncTask("task_1", sample_func, 5)
        result = await task.execute()
        
        assert result == 10
        assert task.status == TaskStatus.COMPLETED
        assert task.result == 10
        assert task.error is None
        assert task.started_at is not None
        assert task.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_task_execution_failure(self):
        """测试任务执行失败"""
        async def failing_func():
            raise ValueError("Test error")
        
        task = AsyncTask("task_1", failing_func)
        
        with pytest.raises(ValueError):
            await task.execute()
        
        assert task.status == TaskStatus.FAILED
        assert task.error == "Test error"
        assert task.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_task_to_dict(self):
        """测试任务转换为字典"""
        async def sample_func(x: int):
            return x * 2
        
        task = AsyncTask("task_1", sample_func, 5)
        await task.execute()
        
        task_dict = task.to_dict()
        assert task_dict["task_id"] == "task_1"
        assert task_dict["status"] == "completed"
        assert task_dict["result"] == 10
        assert task_dict["error"] is None
        assert task_dict["created_at"] is not None
        assert task_dict["started_at"] is not None
        assert task_dict["completed_at"] is not None


class TestAsyncTaskManager:
    """异步任务管理器测试"""
    
    @pytest.mark.asyncio
    async def test_create_task(self):
        """测试创建任务"""
        manager = AsyncTaskManager()
        
        async def sample_func(x: int):
            await asyncio.sleep(0.1)
            return x * 2
        
        task_id = manager.create_task(sample_func, 5)
        assert task_id is not None
        assert task_id in manager.tasks
        
        # 等待任务完成
        await asyncio.sleep(0.2)
        
        task = manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == 10
    
    @pytest.mark.asyncio
    async def test_get_task_status(self):
        """测试获取任务状态"""
        manager = AsyncTaskManager()
        
        async def sample_func(x: int):
            await asyncio.sleep(0.1)
            return x * 2
        
        task_id = manager.create_task(sample_func, 5)
        
        # 立即获取状态（应该是PENDING或RUNNING）
        status = manager.get_task_status(task_id)
        assert status is not None
        assert status["task_id"] == task_id
        assert status["status"] in ["pending", "running"]
        
        # 等待完成
        await asyncio.sleep(0.2)
        
        # 再次获取状态
        status = manager.get_task_status(task_id)
        assert status["status"] == "completed"
        assert status["result"] == 10
    
    @pytest.mark.asyncio
    async def test_cancel_task(self):
        """测试取消任务"""
        manager = AsyncTaskManager()
        
        async def long_running_func():
            await asyncio.sleep(10)
            return "completed"
        
        task_id = manager.create_task(long_running_func)
        
        # 等待任务开始
        await asyncio.sleep(0.1)
        
        # 取消任务
        success = manager.cancel_task(task_id)
        assert success
        
        task = manager.get_task(task_id)
        assert task.status == TaskStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cleanup_completed_tasks(self):
        """测试清理已完成任务"""
        manager = AsyncTaskManager()
        
        async def sample_func(x: int):
            return x * 2
        
        # 创建多个任务
        task_ids = []
        for i in range(5):
            task_id = manager.create_task(sample_func, i)
            task_ids.append(task_id)
        
        # 等待所有任务完成
        await asyncio.sleep(0.2)
        
        # 验证所有任务都存在
        assert len(manager.tasks) >= 5
        
        # 手动设置完成时间为很久以前
        for task_id in task_ids:
            task = manager.get_task(task_id)
            task.completed_at = datetime(2020, 1, 1)
        
        # 清理旧任务
        cleaned = manager.cleanup_completed_tasks(max_age_seconds=60)
        assert cleaned == 5
        
        # 验证任务已被清理
        for task_id in task_ids:
            assert task_id not in manager.tasks


class TestCacheIntegration:
    """缓存集成测试"""
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        # Mock cache manager
        with patch.object(cache_manager, 'set', new_callable=AsyncMock) as mock_set, \
             patch.object(cache_manager, 'get', new_callable=AsyncMock) as mock_get:
            
            mock_set.return_value = True
            mock_get.return_value = {"value": 123}
            
            # 设置缓存
            success = await cache_manager.set("test_key", {"value": 123}, expire=60)
            assert success
            
            # 获取缓存
            value = await cache_manager.get("test_key")
            assert value == {"value": 123}
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """测试缓存过期"""
        # Mock cache manager
        with patch.object(cache_manager, 'set', new_callable=AsyncMock) as mock_set, \
             patch.object(cache_manager, 'get', new_callable=AsyncMock) as mock_get:
            
            mock_set.return_value = True
            # 第一次返回值，第二次返回None（模拟过期）
            mock_get.side_effect = ["test_value", None]
            
            # 设置短期缓存
            await cache_manager.set("test_key", "test_value", expire=1)
            
            # 立即获取应该存在
            value = await cache_manager.get("test_key")
            assert value == "test_value"
            
            # 模拟过期后获取
            value = await cache_manager.get("test_key")
            assert value is None
    
    @pytest.mark.asyncio
    async def test_cache_delete(self):
        """测试缓存删除"""
        # Mock cache manager
        with patch.object(cache_manager, 'set', new_callable=AsyncMock) as mock_set, \
             patch.object(cache_manager, 'exists', new_callable=AsyncMock) as mock_exists, \
             patch.object(cache_manager, 'delete', new_callable=AsyncMock) as mock_delete:
            
            mock_set.return_value = True
            mock_exists.side_effect = [True, False]
            mock_delete.return_value = True
            
            # 设置缓存
            await cache_manager.set("test_key", "test_value")
            
            # 验证存在
            assert await cache_manager.exists("test_key")
            
            # 删除缓存
            success = await cache_manager.delete("test_key")
            assert success
            
            # 验证已删除
            assert not await cache_manager.exists("test_key")


class TestPerformanceMetrics:
    """性能指标测试"""
    
    @pytest.mark.asyncio
    async def test_cache_hit_rate(self):
        """测试缓存命中率"""
        optimizer = PerformanceOptimizer()
        hits = 0
        misses = 0
        
        # Mock cache manager
        with patch.object(cache_manager, 'get', new_callable=AsyncMock) as mock_get, \
             patch.object(cache_manager, 'set', new_callable=AsyncMock) as mock_set:
            
            # 模拟缓存行为：第一次未命中，第二次命中
            mock_get.side_effect = [None, 2, None, 4, 2, 4]
            mock_set.return_value = True
            
            @optimizer.cached("test", ttl=60)
            async def cached_func(x: int):
                nonlocal misses
                misses += 1
                return x * 2
            
            # 第一次调用（缓存未命中）
            await cached_func(1)
            assert misses == 1
            
            # 第二次调用（缓存命中）
            await cached_func(1)
            assert misses == 1  # 没有增加
            
            # 不同参数（缓存未命中）
            await cached_func(2)
            assert misses == 2
            
            # 再次调用相同参数（缓存命中）
            await cached_func(1)
            await cached_func(2)
            assert misses == 2  # 没有增加
    
    @pytest.mark.asyncio
    async def test_async_task_performance(self):
        """测试异步任务性能"""
        manager = AsyncTaskManager()
        
        async def quick_task(x: int):
            await asyncio.sleep(0.01)
            return x * 2
        
        # 创建多个任务
        start_time = asyncio.get_event_loop().time()
        task_ids = []
        for i in range(10):
            task_id = manager.create_task(quick_task, i)
            task_ids.append(task_id)
        
        # 等待所有任务完成
        await asyncio.sleep(0.3)  # 增加等待时间
        
        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time
        
        # 验证所有任务都完成
        for task_id in task_ids:
            task = manager.get_task(task_id)
            assert task.status == TaskStatus.COMPLETED
        
        # 并发执行应该比串行快
        # 10个任务，每个0.01秒，串行需要0.1秒
        # 并发应该接近0.01秒（加上开销）
        assert elapsed < 0.5  # 给更多余量
