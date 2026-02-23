"""订阅管理属性测试（Property-Based Testing）"""
import pytest
from hypothesis import given, settings, strategies as st, assume
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.services.subscription import SubscriptionService
from app.services.auth import AuthenticationService
from app.models.user import SubscriptionTier
from tests.strategies import email_strategy, password_strategy, subscription_tier_strategy


# Feature: short-drama-production-tool, Property 25: 订阅处理
@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy,
    plan=subscription_tier_strategy
)
@settings(max_examples=100)
def test_property_25_subscription_processing(
    db_session: Session,
    email: str,
    password: str,
    plan: SubscriptionTier
):
    """
    属性25：订阅处理
    
    对于任意订阅计划选择，系统应处理支付并激活相应的功能权限
    
    **验证：需求7.4**
    """
    auth_service = AuthenticationService(db_session)
    subscription_service = SubscriptionService(db_session)
    
    try:
        # 注册用户
        user = auth_service.register_user(email, password)
        initial_tier = user.subscription_tier
        initial_quota = user.remaining_quota_minutes
        
        # 激活订阅
        updated_user, subscription = subscription_service.activate_subscription(
            user_id=user.id,
            plan=plan
        )
        
        # 验证订阅创建成功
        assert subscription is not None, "订阅对象不应为None"
        assert subscription.user_id == user.id, "订阅应该属于该用户"
        assert subscription.plan == plan, f"订阅计划应该是{plan}"
        
        # 验证用户权限更新
        assert updated_user.subscription_tier == plan, f"用户订阅层级应该更新为{plan}"
        
        # 验证额度更新（订阅制计划应该增加额度）
        plan_config = subscription_service.SUBSCRIPTION_PLANS[plan]
        if plan in [SubscriptionTier.FREE, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            expected_quota = initial_quota + plan_config["quota_minutes"]
            assert updated_user.remaining_quota_minutes == expected_quota, \
                f"用户额度应该增加到{expected_quota}"
        
        # 验证订阅时间设置
        assert subscription.start_date is not None, "订阅开始时间不应为None"
        assert subscription.end_date is not None, "订阅结束时间不应为None"
        assert subscription.end_date > subscription.start_date, "订阅结束时间应该晚于开始时间"
        
        # 清理
        db_session.delete(subscription)
        db_session.delete(user)
        db_session.commit()
        
    except ValueError as e:
        if "邮箱已被注册" in str(e):
            pytest.skip("邮箱已存在，跳过测试")
        raise


# Feature: short-drama-production-tool, Property 26: 订阅到期处理
@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy,
    plan=subscription_tier_strategy
)
@settings(max_examples=100)
def test_property_26_subscription_expiry_handling(
    db_session: Session,
    email: str,
    password: str,
    plan: SubscriptionTier
):
    """
    属性26：订阅到期处理
    
    对于任意到期的订阅，系统应限制高级功能的访问并提示用户续费
    
    **验证：需求7.5**
    """
    # 跳过按量付费计划（不会过期）
    assume(plan != SubscriptionTier.PAY_PER_USE)
    
    auth_service = AuthenticationService(db_session)
    subscription_service = SubscriptionService(db_session)
    
    try:
        # 注册用户并激活订阅
        user = auth_service.register_user(email, password)
        _, subscription = subscription_service.activate_subscription(
            user_id=user.id,
            plan=plan
        )
        
        # 手动设置订阅为过期
        subscription.end_date = datetime.utcnow() - timedelta(days=1)
        db_session.commit()
        
        # 检查订阅是否过期
        is_expired = subscription_service.check_subscription_expiry(user.id)
        assert is_expired is True, "订阅应该被识别为已过期"
        
        # 处理订阅到期
        updated_user = subscription_service.handle_subscription_expiry(user.id)
        
        # 验证用户降级到免费版
        assert updated_user.subscription_tier == SubscriptionTier.FREE, \
            "过期后用户应该降级到免费版"
        assert updated_user.remaining_quota_minutes == 5.0, \
            "过期后用户额度应该重置为免费版额度（5分钟）"
        
        # 清理
        db_session.delete(subscription)
        db_session.delete(updated_user)
        db_session.commit()
        
    except ValueError as e:
        if "邮箱已被注册" in str(e):
            pytest.skip("邮箱已存在，跳过测试")
        raise


# Feature: short-drama-production-tool, Property 27: 计费模式切换
@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy,
    initial_plan=subscription_tier_strategy,
    new_plan=subscription_tier_strategy
)
@settings(max_examples=100)
def test_property_27_billing_mode_switching(
    db_session: Session,
    email: str,
    password: str,
    initial_plan: SubscriptionTier,
    new_plan: SubscriptionTier
):
    """
    属性27：计费模式切换
    
    对于任意用户，系统应允许在不同计费模式之间切换
    
    **验证：需求7.6**
    """
    # 确保两个计划不同
    assume(initial_plan != new_plan)
    
    auth_service = AuthenticationService(db_session)
    subscription_service = SubscriptionService(db_session)
    
    try:
        # 注册用户并激活初始订阅
        user = auth_service.register_user(email, password)
        subscription_service.activate_subscription(
            user_id=user.id,
            plan=initial_plan
        )
        
        # 验证初始订阅
        db_session.refresh(user)
        assert user.subscription_tier == initial_plan, f"初始订阅应该是{initial_plan}"
        
        # 切换到新计划
        updated_user, new_subscription = subscription_service.switch_subscription_plan(
            user_id=user.id,
            new_plan=new_plan
        )
        
        # 验证切换成功
        assert updated_user.subscription_tier == new_plan, \
            f"用户订阅层级应该切换到{new_plan}"
        assert new_subscription.plan == new_plan, \
            f"新订阅计划应该是{new_plan}"
        
        # 验证旧订阅被终止
        old_subscriptions = subscription_service.get_user_subscriptions(
            user_id=user.id,
            active_only=False
        )
        # 应该至少有2个订阅（旧的和新的）
        assert len(old_subscriptions) >= 2, "应该有多个订阅记录"
        
        # 验证只有一个活跃订阅
        active_subscription = subscription_service.get_active_subscription(user.id)
        assert active_subscription is not None, "应该有一个活跃订阅"
        assert active_subscription.plan == new_plan, "活跃订阅应该是新计划"
        
        # 清理
        for sub in old_subscriptions:
            db_session.delete(sub)
        db_session.delete(user)
        db_session.commit()
        
    except ValueError as e:
        if "邮箱已被注册" in str(e):
            pytest.skip("邮箱已存在，跳过测试")
        raise


@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy,
    plan=subscription_tier_strategy
)
@settings(max_examples=100)
def test_subscription_quota_allocation_property(
    db_session: Session,
    email: str,
    password: str,
    plan: SubscriptionTier
):
    """
    属性：订阅额度分配
    
    对于任意订阅计划，系统应该正确分配相应的额度
    
    **验证：需求7.3, 7.4**
    """
    auth_service = AuthenticationService(db_session)
    subscription_service = SubscriptionService(db_session)
    
    try:
        # 注册用户
        user = auth_service.register_user(email, password)
        initial_quota = user.remaining_quota_minutes
        
        # 激活订阅
        updated_user, subscription = subscription_service.activate_subscription(
            user_id=user.id,
            plan=plan
        )
        
        # 获取计划配置
        plan_config = subscription_service.SUBSCRIPTION_PLANS[plan]
        
        # 验证订阅额度
        assert subscription.quota_minutes == plan_config["quota_minutes"], \
            f"订阅额度应该是{plan_config['quota_minutes']}"
        
        # 验证用户额度更新（订阅制计划）
        if plan in [SubscriptionTier.FREE, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            expected_quota = initial_quota + plan_config["quota_minutes"]
            assert updated_user.remaining_quota_minutes == expected_quota, \
                f"用户额度应该增加到{expected_quota}"
        elif plan == SubscriptionTier.PAY_PER_USE:
            # 按量付费不增加额度
            assert updated_user.remaining_quota_minutes == initial_quota, \
                "按量付费不应该增加额度"
        
        # 清理
        db_session.delete(subscription)
        db_session.delete(user)
        db_session.commit()
        
    except ValueError as e:
        if "邮箱已被注册" in str(e):
            pytest.skip("邮箱已存在，跳过测试")
        raise
