"""用户认证单元测试"""
import pytest
from sqlalchemy.orm import Session

from app.services.auth import AuthenticationService
from app.models.user import User, SubscriptionTier


class TestUserRegistration:
    """用户注册测试"""
    
    def test_register_with_valid_email(self, db_session: Session):
        """测试使用有效邮箱注册"""
        auth_service = AuthenticationService(db_session)
        
        user = auth_service.register_user("test@example.com", "password123")
        
        assert user.email == "test@example.com"
        assert user.subscription_tier == SubscriptionTier.FREE
        assert user.remaining_quota_minutes == 5.0
        assert user.id is not None
        assert user.password_hash != "password123"  # 密码应该被加密
    
    def test_register_with_invalid_email(self, db_session: Session):
        """测试使用无效邮箱注册（由Pydantic在API层验证）"""
        # 这个测试在API层进行，这里测试服务层逻辑
        auth_service = AuthenticationService(db_session)
        
        # 服务层不验证邮箱格式，只检查重复
        user = auth_service.register_user("invalid-email", "password123")
        assert user.email == "invalid-email"
    
    def test_register_with_duplicate_email(self, db_session: Session):
        """测试使用重复邮箱注册"""
        auth_service = AuthenticationService(db_session)
        
        # 第一次注册
        auth_service.register_user("test@example.com", "password123")
        
        # 第二次注册相同邮箱应该失败
        with pytest.raises(ValueError, match="邮箱已被注册"):
            auth_service.register_user("test@example.com", "password456")
    
    def test_password_is_hashed(self, db_session: Session):
        """测试密码被正确加密"""
        auth_service = AuthenticationService(db_session)
        
        user = auth_service.register_user("test@example.com", "password123")
        
        # 密码哈希不应该等于原始密码
        assert user.password_hash != "password123"
        # 密码哈希应该是bcrypt格式
        assert user.password_hash.startswith("$2b$")


class TestUserLogin:
    """用户登录测试"""
    
    def test_login_with_correct_credentials(self, db_session: Session):
        """测试使用正确凭证登录"""
        auth_service = AuthenticationService(db_session)
        
        # 先注册用户
        auth_service.register_user("test@example.com", "password123")
        
        # 登录
        user, token = auth_service.login("test@example.com", "password123")
        
        assert user.email == "test@example.com"
        assert token is not None
        assert len(token) > 0
    
    def test_login_with_wrong_password(self, db_session: Session):
        """测试使用错误密码登录"""
        auth_service = AuthenticationService(db_session)
        
        # 先注册用户
        auth_service.register_user("test@example.com", "password123")
        
        # 使用错误密码登录
        with pytest.raises(ValueError, match="邮箱或密码错误"):
            auth_service.login("test@example.com", "wrongpassword")
    
    def test_login_with_nonexistent_email(self, db_session: Session):
        """测试使用不存在的邮箱登录"""
        auth_service = AuthenticationService(db_session)
        
        with pytest.raises(ValueError, match="邮箱或密码错误"):
            auth_service.login("nonexistent@example.com", "password123")


class TestJWTToken:
    """JWT令牌测试"""
    
    def test_token_generation(self, db_session: Session):
        """测试JWT令牌生成"""
        auth_service = AuthenticationService(db_session)
        
        # 注册并登录
        user = auth_service.register_user("test@example.com", "password123")
        _, token = auth_service.login("test@example.com", "password123")
        
        # 验证令牌
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(user.id)
        assert payload["email"] == user.email
        assert "exp" in payload
    
    def test_token_verification_with_valid_token(self, db_session: Session):
        """测试验证有效令牌"""
        auth_service = AuthenticationService(db_session)
        
        # 注册并登录
        user = auth_service.register_user("test@example.com", "password123")
        _, token = auth_service.login("test@example.com", "password123")
        
        # 使用令牌获取用户
        current_user = auth_service.get_current_user(token)
        
        assert current_user is not None
        assert current_user.id == user.id
        assert current_user.email == user.email
    
    def test_token_verification_with_invalid_token(self, db_session: Session):
        """测试验证无效令牌"""
        auth_service = AuthenticationService(db_session)
        
        # 使用无效令牌
        current_user = auth_service.get_current_user("invalid_token")
        
        assert current_user is None
    
    def test_token_verification_with_expired_token(self, db_session: Session):
        """测试验证过期令牌"""
        from datetime import timedelta
        
        auth_service = AuthenticationService(db_session)
        
        # 注册用户
        user = auth_service.register_user("test@example.com", "password123")
        
        # 创建一个已过期的令牌（-1秒）
        expired_token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(seconds=-1)
        )
        
        # 验证过期令牌应该失败
        current_user = auth_service.get_current_user(expired_token)
        assert current_user is None


class TestPasswordEncryption:
    """密码加密测试"""
    
    def test_password_hashing(self, db_session: Session):
        """测试密码哈希生成"""
        auth_service = AuthenticationService(db_session)
        
        password = "testpassword123"
        hashed = auth_service.get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
    
    def test_password_verification(self, db_session: Session):
        """测试密码验证"""
        auth_service = AuthenticationService(db_session)
        
        password = "testpassword123"
        hashed = auth_service.get_password_hash(password)
        
        # 正确密码应该验证成功
        assert auth_service.verify_password(password, hashed) is True
        
        # 错误密码应该验证失败
        assert auth_service.verify_password("wrongpassword", hashed) is False
    
    def test_same_password_different_hashes(self, db_session: Session):
        """测试相同密码生成不同哈希（salt）"""
        auth_service = AuthenticationService(db_session)
        
        password = "testpassword123"
        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)
        
        # 由于使用了salt，相同密码应该生成不同的哈希
        assert hash1 != hash2
        
        # 但两个哈希都应该能验证原始密码
        assert auth_service.verify_password(password, hash1) is True
        assert auth_service.verify_password(password, hash2) is True
