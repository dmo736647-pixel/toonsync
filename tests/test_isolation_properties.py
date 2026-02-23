"""用户操作隔离属性测试

Feature: short-drama-production-tool
Property 46: 用户操作隔离性
"""
import pytest
from hypothesis import given, settings, strategies as st
from unittest.mock import Mock

from app.services.isolation import (
    RateLimiter,
    ErrorIsolation,
    DataIsolation,
    ResourceLimiter
)


# 测试策略
@st.composite
def user_id_strategy(draw):
    """生成用户ID"""
    return f"user_{draw(st.integers(min_value=1, max_value=100))}"


@st.composite
def request_sequence_strategy(draw):
    """生成请求序列"""
    return draw(st.lists(
        st.integers(min_value=1, max_value=10),
        min_size=1,
        max_size=50
    ))


class TestIsolationProperties:
    """隔离性属性测试"""
    
    # Feature: short-drama-production-tool, Property 46: 用户操作隔离性
    @given(
        user1_requests=st.integers(min_value=1, max_value=100),
        user2_requests=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    def test_user_isolation_property(self, user1_requests, user2_requests):
        """
        属性46：对于任意单个用户的操作失败，系统应不影响其他用户的正常使用
        
        **验证：需求12.5**
        
        测试策略：
        1. 用户1进行大量请求直到被限制
        2. 验证用户2不受影响
        """
        limiter = RateLimiter()
        
        # 用户1进行请求
        user1_allowed_count = 0
        for i in range(user1_requests):
            allowed, _ = limiter.check_rate_limit("user_1", "api")
            if allowed:
                user1_allowed_count += 1
        
        # 用户2应该不受影响
        user2_allowed, _ = limiter.check_rate_limit("user_2", "api")
        assert user2_allowed, "用户2应该不受用户1的限制影响"
        
        # 验证用户2有完整的配额
        user2_remaining = limiter.get_remaining_quota("user_2", "api")
        assert user2_remaining > 50, f"用户2的配额应该接近满额，实际剩余{user2_remaining}"
    
    @given(
        error_count=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=100)
    def test_error_isolation_property(self, error_count):
        """
        属性：错误隔离
        
        对于任意用户的错误，不应影响其他用户
        
        **验证：需求12.5**
        """
        isolation = ErrorIsolation()
        
        # 用户1产生错误
        for i in range(error_count):
            isolation.record_error("user_1", Exception(f"Error {i}"))
        
        # 检查用户1的状态
        user1_isolated = isolation.should_isolate("user_1")
        user1_error_count = isolation.get_error_count("user_1")
        
        # 用户2不应该受影响
        user2_isolated = isolation.should_isolate("user_2")
        user2_error_count = isolation.get_error_count("user_2")
        
        assert not user2_isolated, "用户2不应该被隔离"
        assert user2_error_count == 0, "用户2的错误计数应该为0"
        
        # 如果用户1错误很多，应该被隔离
        if error_count >= 10:
            assert user1_isolated, f"用户1有{error_count}个错误，应该被隔离"
    
    @given(
        user_count=st.integers(min_value=2, max_value=10),
        requests_per_user=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=50)
    def test_multi_user_isolation_property(self, user_count, requests_per_user):
        """
        属性：多用户隔离
        
        对于任意数量的用户，每个用户的操作应该独立
        
        **验证：需求12.5**
        """
        limiter = RateLimiter()
        
        # 每个用户进行请求
        user_results = {}
        for user_idx in range(user_count):
            user_id = f"user_{user_idx}"
            allowed_count = 0
            
            for req_idx in range(requests_per_user):
                allowed, _ = limiter.check_rate_limit(user_id, "api")
                if allowed:
                    allowed_count += 1
            
            user_results[user_id] = allowed_count
        
        # 验证每个用户的结果
        for user_id, allowed_count in user_results.items():
            # 每个用户应该至少有一些请求被允许
            assert allowed_count > 0, f"{user_id}应该有请求被允许"
            
            # 如果请求数在限制内，应该全部被允许
            if requests_per_user <= 60:  # API限制是60/分钟
                assert allowed_count == requests_per_user, \
                    f"{user_id}的{requests_per_user}个请求应该全部被允许"
    
    @given(
        resource_amount=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    def test_resource_isolation_property(self, resource_amount):
        """
        属性：资源隔离
        
        对于任意用户的资源使用，不应影响其他用户的资源配额
        
        **验证：需求12.5**
        """
        limiter = ResourceLimiter()
        
        # 用户1使用资源
        for i in range(resource_amount):
            limiter.check_resource_limit("user_1", "requests", 1)
        
        # 获取用户1的使用情况
        user1_usage = limiter.get_resource_usage("user_1")
        
        # 用户2的资源应该独立
        user2_usage = limiter.get_resource_usage("user_2")
        
        assert user1_usage["requests"] == resource_amount
        assert user2_usage["requests"] == 0, "用户2的资源使用应该为0"
        
        # 用户2应该有完整的配额
        user2_allowed = limiter.check_resource_limit("user_2", "requests", 1)
        assert user2_allowed, "用户2应该可以使用资源"
    
    @given(
        owner_id=user_id_strategy(),
        other_id=user_id_strategy()
    )
    @settings(max_examples=100)
    def test_data_isolation_property(self, owner_id, other_id):
        """
        属性：数据隔离
        
        对于任意资源，只有所有者和授权用户可以访问
        
        **验证：需求12.5**
        """
        # 假设owner_id和other_id不同
        if owner_id == other_id:
            return
        
        # 创建资源
        resource = Mock()
        resource.user_id = owner_id
        resource.collaborators = []
        
        # 所有者可以访问
        assert DataIsolation.can_access(resource, owner_id), \
            "所有者应该可以访问自己的资源"
        
        # 其他用户不能访问
        assert not DataIsolation.can_access(resource, other_id), \
            "未授权用户不应该可以访问资源"
        
        # 验证所有权
        assert DataIsolation.verify_ownership(resource, owner_id)
        assert not DataIsolation.verify_ownership(resource, other_id)


class TestRateLimitProperties:
    """速率限制属性测试"""
    
    @given(
        request_count=st.integers(min_value=1, max_value=200)
    )
    @settings(max_examples=100)
    def test_rate_limit_fairness_property(self, request_count):
        """
        属性：速率限制公平性
        
        对于任意请求数量，速率限制应该公平地应用
        
        **验证：需求12.5**
        """
        limiter = RateLimiter()
        user_id = f"test_user_{request_count}"
        
        allowed_count = 0
        denied_count = 0
        
        for i in range(request_count):
            allowed, _ = limiter.check_rate_limit(user_id, "api")
            if allowed:
                allowed_count += 1
            else:
                denied_count += 1
        
        # 验证限制逻辑
        if request_count <= 60:
            # 在限制内，应该全部允许
            assert allowed_count == request_count
            assert denied_count == 0
        else:
            # 超过限制，应该有部分被拒绝
            assert allowed_count == 60  # API限制
            assert denied_count == request_count - 60
    
    @given(
        user_ids=st.lists(user_id_strategy(), min_size=2, max_size=5, unique=True)
    )
    @settings(max_examples=50)
    def test_rate_limit_independence_property(self, user_ids):
        """
        属性：速率限制独立性
        
        对于任意多个用户，每个用户的速率限制应该独立
        
        **验证：需求12.5**
        """
        limiter = RateLimiter()
        
        # 第一个用户用完配额
        first_user = user_ids[0]
        for i in range(60):
            limiter.check_rate_limit(first_user, "api")
        
        # 第一个用户应该被限制
        allowed, _ = limiter.check_rate_limit(first_user, "api")
        assert not allowed, f"{first_user}应该被限制"
        
        # 其他用户不应该受影响
        for user_id in user_ids[1:]:
            allowed, _ = limiter.check_rate_limit(user_id, "api")
            assert allowed, f"{user_id}不应该受{first_user}的影响"


class TestErrorIsolationProperties:
    """错误隔离属性测试"""
    
    @given(
        error_counts=st.lists(
            st.integers(min_value=0, max_value=15),
            min_size=2,
            max_size=5
        )
    )
    @settings(max_examples=50)
    def test_error_isolation_independence_property(self, error_counts):
        """
        属性：错误隔离独立性
        
        对于任意多个用户的错误，每个用户的隔离状态应该独立
        
        **验证：需求12.5**
        """
        isolation = ErrorIsolation()
        
        # 为每个用户记录错误
        for idx, count in enumerate(error_counts):
            user_id = f"user_{idx}"
            for i in range(count):
                isolation.record_error(user_id, Exception(f"Error {i}"))
        
        # 验证每个用户的隔离状态
        for idx, count in enumerate(error_counts):
            user_id = f"user_{idx}"
            should_isolate = isolation.should_isolate(user_id)
            error_count = isolation.get_error_count(user_id)
            
            assert error_count == count
            
            # 只有错误数>=10的用户应该被隔离
            if count >= 10:
                assert should_isolate, f"{user_id}有{count}个错误，应该被隔离"
            else:
                assert not should_isolate, f"{user_id}只有{count}个错误，不应该被隔离"
