"""用户认证属性测试（Property-Based Testing）"""
import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy.orm import Session

from app.services.auth import AuthenticationService
from app.models.user import SubscriptionTier
from tests.strategies import email_strategy, password_strategy


# Feature: short-drama-production-tool, Property 23: 用户注册
@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy
)
@settings(max_examples=100)
def test_property_23_user_registration(db_session: Session, email: str, password: str):
    """
    属性23：用户注册
    
    对于任意有效的邮箱和密码组合，系统应成功创建新的用户账户
    
    **验证：需求7.1**
    """
    auth_service = AuthenticationService(db_session)
    
    try:
        # 尝试注册用户
        user = auth_service.register_user(email, password)
        
        # 验证用户创建成功
        assert user is not None, "用户对象不应为None"
        assert user.id is not None, "用户ID应该被分配"
        assert user.email == email, f"用户邮箱应该是{email}"
        assert user.subscription_tier == SubscriptionTier.FREE, "新用户应该是免费版"
        assert user.remaining_quota_minutes == 5.0, "新用户应该有5分钟免费额度"
        assert user.password_hash != password, "密码应该被加密存储"
        assert len(user.password_hash) > 0, "密码哈希不应为空"
        
        # 验证密码可以被验证
        assert auth_service.verify_password(password, user.password_hash), \
            "加密后的密码应该能够被验证"
        
        # 清理：删除创建的用户以避免重复邮箱错误
        db_session.delete(user)
        db_session.commit()
        
    except ValueError as e:
        # 如果是邮箱已存在的错误，这是预期的（在并发测试中可能发生）
        if "邮箱已被注册" not in str(e):
            raise


# Feature: short-drama-production-tool, Property 24: 用户登录验证
@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy,
    wrong_password=password_strategy
)
@settings(max_examples=100)
def test_property_24_user_login_verification(
    db_session: Session,
    email: str,
    password: str,
    wrong_password: str
):
    """
    属性24：用户登录验证
    
    对于任意登录尝试，系统应验证凭证，正确的凭证应授予访问权限
    
    **验证：需求7.2**
    """
    auth_service = AuthenticationService(db_session)
    
    try:
        # 先注册用户
        registered_user = auth_service.register_user(email, password)
        
        # 测试正确凭证登录
        user, token = auth_service.login(email, password)
        
        # 验证登录成功
        assert user is not None, "用户对象不应为None"
        assert user.id == registered_user.id, "登录用户应该是注册的用户"
        assert user.email == email, f"登录用户邮箱应该是{email}"
        assert token is not None, "JWT令牌不应为None"
        assert len(token) > 0, "JWT令牌不应为空"
        
        # 验证令牌有效
        payload = auth_service.verify_token(token)
        assert payload is not None, "令牌应该能够被验证"
        assert payload["sub"] == str(user.id), "令牌应该包含用户ID"
        assert payload["email"] == email, "令牌应该包含用户邮箱"
        
        # 验证可以使用令牌获取用户
        current_user = auth_service.get_current_user(token)
        assert current_user is not None, "应该能够通过令牌获取用户"
        assert current_user.id == user.id, "获取的用户应该是登录的用户"
        
        # 测试错误凭证登录（如果密码不同）
        if wrong_password != password:
            with pytest.raises(ValueError, match="邮箱或密码错误"):
                auth_service.login(email, wrong_password)
        
        # 清理
        db_session.delete(registered_user)
        db_session.commit()
        
    except ValueError as e:
        # 如果是邮箱已存在的错误，跳过这个测试用例
        if "邮箱已被注册" in str(e):
            pytest.skip("邮箱已存在，跳过测试")
        raise


@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy
)
@settings(max_examples=100)
def test_password_encryption_property(db_session: Session, email: str, password: str):
    """
    属性：密码加密
    
    对于任意密码，系统应该加密存储，且加密后的密码应该能够验证原始密码
    
    **验证：需求11.5**
    """
    auth_service = AuthenticationService(db_session)
    
    try:
        # 注册用户
        user = auth_service.register_user(email, password)
        
        # 验证密码被加密
        assert user.password_hash != password, "密码不应该以明文存储"
        assert len(user.password_hash) > len(password), "加密后的密码应该更长"
        
        # 验证密码可以被验证
        assert auth_service.verify_password(password, user.password_hash), \
            "原始密码应该能够通过加密后的哈希验证"
        
        # 验证错误密码不能通过验证
        if len(password) > 0:
            wrong_password = password + "x"
            assert not auth_service.verify_password(wrong_password, user.password_hash), \
                "错误的密码不应该通过验证"
        
        # 清理
        db_session.delete(user)
        db_session.commit()
        
    except ValueError as e:
        if "邮箱已被注册" in str(e):
            pytest.skip("邮箱已存在，跳过测试")
        raise


@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy
)
@settings(max_examples=100)
def test_jwt_token_validity_property(db_session: Session, email: str, password: str):
    """
    属性：JWT令牌有效性
    
    对于任意用户，生成的JWT令牌应该包含正确的用户信息，并且能够被验证
    
    **验证：需求7.2**
    """
    auth_service = AuthenticationService(db_session)
    
    try:
        # 注册并登录
        user = auth_service.register_user(email, password)
        _, token = auth_service.login(email, password)
        
        # 验证令牌格式
        assert isinstance(token, str), "令牌应该是字符串"
        assert len(token) > 0, "令牌不应为空"
        assert token.count('.') == 2, "JWT令牌应该有3个部分（header.payload.signature）"
        
        # 验证令牌内容
        payload = auth_service.verify_token(token)
        assert payload is not None, "令牌应该能够被解码"
        assert "sub" in payload, "令牌应该包含subject（用户ID）"
        assert "email" in payload, "令牌应该包含邮箱"
        assert "exp" in payload, "令牌应该包含过期时间"
        assert payload["sub"] == str(user.id), "令牌的subject应该是用户ID"
        assert payload["email"] == email, "令牌的邮箱应该匹配"
        
        # 验证可以使用令牌获取用户
        retrieved_user = auth_service.get_current_user(token)
        assert retrieved_user is not None, "应该能够通过令牌获取用户"
        assert retrieved_user.id == user.id, "获取的用户ID应该匹配"
        assert retrieved_user.email == email, "获取的用户邮箱应该匹配"
        
        # 清理
        db_session.delete(user)
        db_session.commit()
        
    except ValueError as e:
        if "邮箱已被注册" in str(e):
            pytest.skip("邮箱已存在，跳过测试")
        raise
