"""订阅管理单元测试"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.subscription import SubscriptionService
from app.services.auth import AuthenticationService
from app.models.user import User, SubscriptionTier


class TestSubscriptionCreation:
    """订阅创建测试"""
    
    def test_create_subscription_with_valid_plan(self, db_session: Session):
        """测试创建有效订阅"""
        # 创建用户
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        # 创建订阅
        subscription_service = SubscriptionService(db_session)
        subscription = subscription_service.create_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        
        assert subscription.user_id == user.id
        assert subscription.plan == SubscriptionTier.PROFESSIONAL
        assert subscription.quota_minutes == 50.0
        assert subscription.auto_renew is True
        assert subscription.start_date is not None
        assert subscription.end_date > subscription.start_date
    
    def test_create_subscription_with_invalid_user(self, db_session: Session):
        """测试为不存在的用户创建订阅"""
        import uuid
        
        subscription_service = SubscriptionService(db_session)
        
        with pytest.raises(ValueError, match="用户不存在"):
            subscription_service.create_subscription(
                user_id=uuid.uuid4(),
                plan=SubscriptionTier.PROFESSIONAL
            )


class TestSubscriptionActivation:
    """订阅激活测试"""
    
    def test_activate_subscription(self, db_session: Session):
        """测试激活订阅"""
        # 创建用户
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        initial_quota = user.remaining_quota_minutes
        
        # 激活订阅
        subscription_service = SubscriptionService(db_session)
        updated_user, subscription = subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        
        # 验证用户订阅层级更新
        assert updated_user.subscription_tier == SubscriptionTier.PROFESSIONAL
        # 验证额度增加
        assert updated_user.remaining_quota_minutes == initial_quota + 50.0
        # 验证订阅创建
        assert subscription.plan == SubscriptionTier.PROFESSIONAL
    
    def test_activate_pay_per_use_subscription(self, db_session: Session):
        """测试激活按量付费订阅"""
        # 创建用户
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        initial_quota = user.remaining_quota_minutes
        
        # 激活按量付费订阅
        subscription_service = SubscriptionService(db_session)
        updated_user, subscription = subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PAY_PER_USE
        )
        
        # 验证用户订阅层级更新
        assert updated_user.subscription_tier == SubscriptionTier.PAY_PER_USE
        # 按量付费不增加额度
        assert updated_user.remaining_quota_minutes == initial_quota


class TestSubscriptionExpiry:
    """订阅到期测试"""
    
    def test_check_subscription_expiry_with_active_subscription(self, db_session: Session):
        """测试检查活跃订阅"""
        # 创建用户并激活订阅
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        subscription_service = SubscriptionService(db_session)
        subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        
        # 检查订阅是否过期
        is_expired = subscription_service.check_subscription_expiry(user.id)
        
        assert is_expired is False
    
    def test_check_subscription_expiry_without_subscription(self, db_session: Session):
        """测试检查无订阅用户"""
        # 创建用户但不激活订阅
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        subscription_service = SubscriptionService(db_session)
        
        # 检查订阅是否过期
        is_expired = subscription_service.check_subscription_expiry(user.id)
        
        assert is_expired is True
    
    def test_handle_subscription_expiry(self, db_session: Session):
        """测试处理订阅到期"""
        # 创建用户并激活订阅
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        subscription_service = SubscriptionService(db_session)
        _, subscription = subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        
        # 手动设置订阅为过期
        subscription.end_date = datetime.utcnow() - timedelta(days=1)
        db_session.commit()
        
        # 处理订阅到期
        updated_user = subscription_service.handle_subscription_expiry(user.id)
        
        # 验证用户降级到免费版
        assert updated_user.subscription_tier == SubscriptionTier.FREE
        assert updated_user.remaining_quota_minutes == 5.0


class TestSubscriptionPlanSwitch:
    """订阅计划切换测试"""
    
    def test_switch_subscription_plan(self, db_session: Session):
        """测试切换订阅计划"""
        # 创建用户并激活专业版订阅
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        subscription_service = SubscriptionService(db_session)
        subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        
        # 切换到企业版
        updated_user, new_subscription = subscription_service.switch_subscription_plan(
            user_id=user.id,
            new_plan=SubscriptionTier.ENTERPRISE
        )
        
        # 验证用户订阅层级更新
        assert updated_user.subscription_tier == SubscriptionTier.ENTERPRISE
        # 验证新订阅创建
        assert new_subscription.plan == SubscriptionTier.ENTERPRISE
        assert new_subscription.quota_minutes == 200.0
    
    def test_switch_from_free_to_professional(self, db_session: Session):
        """测试从免费版切换到专业版"""
        # 创建免费版用户
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        assert user.subscription_tier == SubscriptionTier.FREE
        
        # 切换到专业版
        subscription_service = SubscriptionService(db_session)
        updated_user, subscription = subscription_service.switch_subscription_plan(
            user_id=user.id,
            new_plan=SubscriptionTier.PROFESSIONAL
        )
        
        # 验证切换成功
        assert updated_user.subscription_tier == SubscriptionTier.PROFESSIONAL


class TestSubscriptionPermissions:
    """订阅权限验证测试"""
    
    def test_get_subscription_plans(self, db_session: Session):
        """测试获取订阅计划"""
        subscription_service = SubscriptionService(db_session)
        plans = subscription_service.get_subscription_plans()
        
        # 验证所有计划都存在
        assert SubscriptionTier.FREE in plans
        assert SubscriptionTier.PAY_PER_USE in plans
        assert SubscriptionTier.PROFESSIONAL in plans
        assert SubscriptionTier.ENTERPRISE in plans
        
        # 验证计划配置
        assert plans[SubscriptionTier.FREE]["quota_minutes"] == 5.0
        assert plans[SubscriptionTier.PROFESSIONAL]["quota_minutes"] == 50.0
        assert plans[SubscriptionTier.ENTERPRISE]["quota_minutes"] == 200.0
    
    def test_get_user_subscriptions(self, db_session: Session):
        """测试获取用户订阅列表"""
        # 创建用户并激活多个订阅
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        subscription_service = SubscriptionService(db_session)
        subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        
        # 获取订阅列表
        subscriptions = subscription_service.get_user_subscriptions(user.id)
        
        assert len(subscriptions) > 0
        assert subscriptions[0].user_id == user.id
    
    def test_get_active_subscription(self, db_session: Session):
        """测试获取活跃订阅"""
        # 创建用户并激活订阅
        auth_service = AuthenticationService(db_session)
        user = auth_service.register_user("test@example.com", "password123")
        
        subscription_service = SubscriptionService(db_session)
        subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        
        # 获取活跃订阅
        active_subscription = subscription_service.get_active_subscription(user.id)
        
        assert active_subscription is not None
        assert active_subscription.plan == SubscriptionTier.PROFESSIONAL
        assert active_subscription.end_date > datetime.utcnow()
