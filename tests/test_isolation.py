"""用户操作隔离单元测试"""
import pytest
import time
from unittest.mock import Mock

from app.services.isolation import (
    RateLimiter,
    ErrorIsolation,
    DataIsolation,
    ResourceLimiter,
    rate_limiter,
    error_isolation,
    data_isolation,
    resource_limiter
)


class TestRateLimiter:
    """速率限制器测试"""
    
    def test_rate_limit_within_quota(self):
        """测试配额内的请求"""
        limiter = RateLimiter()
        user_id = "test_user_1"
        
        # 前几个请求应该被允许
        for i in range(5):
            allowed, wait_time = limiter.check_rate_limit(user_id, "export")
            assert allowed
            assert wait_time is None
    
    def test_rate_limit_exceeded(self):
        """测试超出配额的请求"""
        limiter = RateLimiter()
        user_id = "test_user_2"
        
        # 导出限制：每5分钟5个请求
        for i in range(5):
            allowed, _ = limiter.check_rate_limit(user_id, "export")
            assert allowed
        
        # 第6个请求应该被拒绝
        allowed, wait_time = limiter.check_rate_limit(user_id, "export")
        assert not allowed
        assert wait_time is not None
        assert wait_time > 0
    
    def test_get_remaining_quota(self):
        """测试获取剩余配额"""
        limiter = RateLimiter()
        user_id = "test_user_3"
        
        # 初始配额
        remaining = limiter.get_remaining_quota(user_id, "api")
        assert remaining == 60  # API限制：每分钟60个
        
        # 使用一些配额
        for i in range(10):
            limiter.check_rate_limit(user_id, "api")
        
        remaining = limiter.get_remaining_quota(user_id, "api")
        assert remaining == 50
    
    def test_rate_limit_different_types(self):
        """测试不同类型的速率限制"""
        limiter = RateLimiter()
        user_id = "test_user_4"
        
        # API限制：每分钟60个
        for i in range(60):
            allowed, _ = limiter.check_rate_limit(user_id, "api")
            assert allowed
        
        # 第61个API请求应该被拒绝
        allowed, _ = limiter.check_rate_limit(user_id, "api")
        assert not allowed
        
        # 上传请求使用不同的用户ID来测试独立性
        upload_user = "test_user_4_upload"
        allowed, _ = limiter.check_rate_limit(upload_user, "upload")
        assert allowed


class TestErrorIsolation:
    """错误隔离测试"""
    
    def test_record_error(self):
        """测试记录错误"""
        isolation = ErrorIsolation()
        user_id = "test_user_5"
        
        # 记录错误
        error = ValueError("Test error")
        isolation.record_error(user_id, error)
        
        # 验证错误计数
        count = isolation.get_error_count(user_id)
        assert count == 1
    
    def test_should_not_isolate_few_errors(self):
        """测试少量错误不应该被隔离"""
        isolation = ErrorIsolation()
        user_id = "test_user_6"
        
        # 记录少量错误
        for i in range(5):
            isolation.record_error(user_id, ValueError(f"Error {i}"))
        
        # 不应该被隔离
        assert not isolation.should_isolate(user_id)
    
    def test_should_isolate_many_errors(self):
        """测试大量错误应该被隔离"""
        isolation = ErrorIsolation()
        user_id = "test_user_7"
        
        # 记录大量错误
        for i in range(10):
            isolation.record_error(user_id, ValueError(f"Error {i}"))
        
        # 应该被隔离
        assert isolation.should_isolate(user_id)
    
    def test_error_count(self):
        """测试错误计数"""
        isolation = ErrorIsolation()
        user_id = "test_user_8"
        
        # 记录错误
        for i in range(7):
            isolation.record_error(user_id, ValueError(f"Error {i}"))
        
        # 验证计数
        count = isolation.get_error_count(user_id)
        assert count == 7


class TestDataIsolation:
    """数据隔离测试"""
    
    def test_verify_ownership(self):
        """测试验证资源所有权"""
        # 创建模拟资源
        resource = Mock()
        resource.user_id = "user_123"
        
        # 所有者应该通过验证
        assert DataIsolation.verify_ownership(resource, "user_123")
        
        # 非所有者不应该通过验证
        assert not DataIsolation.verify_ownership(resource, "user_456")
    
    def test_can_access_owner(self):
        """测试所有者可以访问资源"""
        resource = Mock()
        resource.user_id = "user_123"
        resource.collaborators = []
        
        # 所有者可以访问
        assert DataIsolation.can_access(resource, "user_123")
    
    def test_can_access_collaborator(self):
        """测试协作者可以访问资源"""
        resource = Mock()
        resource.user_id = "user_123"
        
        # 创建协作者
        collaborator = Mock()
        collaborator.user_id = "user_456"
        resource.collaborators = [collaborator]
        
        # 协作者可以访问
        assert DataIsolation.can_access(resource, "user_456")
    
    def test_cannot_access_unauthorized(self):
        """测试未授权用户不能访问资源"""
        resource = Mock()
        resource.user_id = "user_123"
        resource.collaborators = []
        
        # 未授权用户不能访问
        assert not DataIsolation.can_access(resource, "user_789")
    
    def test_add_user_filter(self):
        """测试添加用户过滤条件"""
        # 创建模拟查询和模型
        mock_query = Mock()
        mock_model = Mock()
        mock_model.user_id = "field"
        
        # 添加过滤条件
        filtered_query = DataIsolation.add_user_filter(
            mock_query,
            "user_123",
            mock_model
        )
        
        # 验证filter被调用
        mock_query.filter.assert_called_once()


class TestResourceLimiter:
    """资源限制器测试"""
    
    def test_check_resource_limit_within_quota(self):
        """测试配额内的资源使用"""
        limiter = ResourceLimiter()
        user_id = "test_user_9"
        
        # 使用少量资源
        allowed = limiter.check_resource_limit(user_id, "requests", 10)
        assert allowed
    
    def test_check_resource_limit_exceeded(self):
        """测试超出配额的资源使用"""
        limiter = ResourceLimiter()
        user_id = "test_user_10"
        
        # 使用大量资源
        for i in range(100):
            limiter.check_resource_limit(user_id, "requests", 10)
        
        # 超出配额
        allowed = limiter.check_resource_limit(user_id, "requests", 10)
        assert not allowed
    
    def test_get_resource_usage(self):
        """测试获取资源使用情况"""
        limiter = ResourceLimiter()
        user_id = "test_user_11"
        
        # 使用一些资源
        limiter.check_resource_limit(user_id, "requests", 50)
        limiter.check_resource_limit(user_id, "cpu_time", 10.5)
        
        # 获取使用情况
        usage = limiter.get_resource_usage(user_id)
        
        assert usage["requests"] == 50
        assert usage["cpu_time"] == 10.5
        assert "limits" in usage
        assert "reset_in" in usage
    
    def test_resource_limit_cpu_time(self):
        """测试CPU时间限制"""
        limiter = ResourceLimiter()
        user_id = "test_user_12"
        
        # 使用大量CPU时间
        allowed = limiter.check_resource_limit(user_id, "cpu_time", 250)
        assert allowed
        
        # 再使用一些，应该超出限制
        allowed = limiter.check_resource_limit(user_id, "cpu_time", 100)
        assert not allowed
    
    def test_resource_limit_memory(self):
        """测试内存限制"""
        limiter = ResourceLimiter()
        user_id = "test_user_13"
        
        # 使用内存
        allowed = limiter.check_resource_limit(
            user_id,
            "memory",
            500 * 1024 * 1024  # 500MB
        )
        assert allowed
        
        # 再使用，应该超出限制
        allowed = limiter.check_resource_limit(
            user_id,
            "memory",
            600 * 1024 * 1024  # 600MB
        )
        assert not allowed


class TestIsolationIntegration:
    """隔离机制集成测试"""
    
    def test_rate_limit_and_error_isolation(self):
        """测试速率限制和错误隔离的配合"""
        limiter = RateLimiter()
        isolation = ErrorIsolation()
        user_id = "test_user_14"
        
        # 用户频繁请求
        for i in range(10):
            allowed, _ = limiter.check_rate_limit(user_id, "api")
            if not allowed:
                # 如果被限制，记录为错误
                isolation.record_error(user_id, Exception("Rate limit exceeded"))
        
        # 验证状态
        remaining = limiter.get_remaining_quota(user_id, "api")
        assert remaining < 60
    
    def test_multiple_users_isolation(self):
        """测试多用户隔离"""
        limiter = RateLimiter()
        
        # 用户1使用配额
        for i in range(60):
            limiter.check_rate_limit("user_1", "api")
        
        # 用户1应该被限制
        allowed, _ = limiter.check_rate_limit("user_1", "api")
        assert not allowed
        
        # 但用户2不应该受影响
        allowed, _ = limiter.check_rate_limit("user_2", "api")
        assert allowed
    
    def test_resource_and_rate_limit(self):
        """测试资源限制和速率限制的配合"""
        rate_lim = RateLimiter()
        res_lim = ResourceLimiter()
        user_id = "test_user_15"
        
        # 同时检查两种限制
        for i in range(50):
            rate_allowed, _ = rate_lim.check_rate_limit(user_id, "api")
            res_allowed = res_lim.check_resource_limit(user_id, "requests", 1)
            
            # 两者都应该允许
            assert rate_allowed
            assert res_allowed
        
        # 验证使用情况
        rate_remaining = rate_lim.get_remaining_quota(user_id, "api")
        res_usage = res_lim.get_resource_usage(user_id)
        
        assert rate_remaining == 10  # 60 - 50
        assert res_usage["requests"] == 50
