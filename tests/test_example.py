"""示例测试文件"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tests.strategies import user_data_strategy, project_data_strategy


class TestExample:
    """示例测试类"""
    
    @pytest.mark.unit
    def test_basic_example(self):
        """基础单元测试示例"""
        assert 1 + 1 == 2
    
    @pytest.mark.unit
    def test_api_health_check(self, client):
        """API健康检查测试"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    @pytest.mark.property
    @given(email=st.emails())
    @settings(max_examples=100)
    def test_email_validation_property(self, email: str):
        """
        属性测试示例：邮箱验证
        
        对于任意有效的邮箱地址，应包含@符号
        """
        assert "@" in email
    
    @pytest.mark.property
    @given(user_data=user_data_strategy())
    @settings(max_examples=50)
    def test_user_data_structure_property(self, user_data: dict):
        """
        属性测试示例：用户数据结构
        
        对于任意生成的用户数据，应包含必需字段
        """
        assert "email" in user_data
        assert "password" in user_data
        assert "subscription_tier" in user_data
        assert "remaining_quota_minutes" in user_data
        assert user_data["remaining_quota_minutes"] >= 0
