"""额度管理属性测试（Property-Based Testing）"""
import pytest
from hypothesis import given, settings, strategies as st, assume
from sqlalchemy.orm import Session

from app.services.usage import UsageService
from app.services.auth import AuthenticationService
from app.services.subscription import SubscriptionService
from app.models.user import SubscriptionTier
from tests.strategies import email_strategy, password_strategy


# Feature: short-drama-production-tool, Property 28: 额度和统计显示
@pytest.mark.property
@given(
    email=email_strategy,
    password=password_strategy,
    usage_duration=st.floats(min_value=0.1, max_value=10.0)
)
@settings(max_examples=100)
def test_property_28_quota_and_statistics_display(
    db_session: Session,
    email: str,
    password: str,
    usage_duration: float
):
    """
    属性28：额度和统计显示
    
    对于任意用户，系统应实时显示剩余额度和使用统计
    
    **验证：需求7.7**
    """
    auth_service = AuthenticationService(db_session)
    usage_service = UsageService(db_session)
    
    try:
        # 注册用户
        user = auth_service.register_user(email, password)
        initial_quota = user.remaining_quota_minutes
        
        # 确保有足够的额度进行测试
        assume(initial_quota >= usage_duration)
        
        # 扣减额度
        updated_user, cost = usage_service.deduct_quota(
            user_id=user.id,
            duration_minutes=usage_duration,
            action_type="test_action"
        )
        
        # 验证剩余额度实时更新
        expected_remaining = initial_quota - usage_duration
        assert abs(updated_user.remaining_quota_minutes - expected_remaining) < 0.01, \
            f"剩余额度应该是{expected_remaining}，实际是{updated_user.remaining_quota_minutes}"
        
        # 获取使用统计
        statistics = usage_service.get_usage_statistics(
            user_id=user.id,
            days=30
        )
        
        # 验证统计信息包含必要字段
        assert "user_id" in statistics, "统计应该包含用户ID"
        assert "subscription_tier" in statistics, "统计应该包含订阅层级"
        assert "remaining_quota_minutes" in statistics, "统计应该包含剩余额度"
        assert "total_usage_minutes" in statistics, "统计应该包含总使用时长"
        assert "usage_count" in statistics, "统计应该包含使用次数"
        assert "by_action_type" in statistics, "统计应该包含按操作类型分组的数据"
        
        # 验证统计数据准确性
        assert statistics["remaining_quota_minutes"] == updated_user.remaining_quota_minutes, \
            "统计中的剩余额度应该与用户实际剩余额度一致"
        assert statistics["total_usage_minutes"] >= usage_duration, \
            f"统计的总使用时长应该至少包含本次使用的{usage_duration}分钟"
        assert statistics["usage_count"] >= 1, "使用次数应该至少为1"
        
        # 验证按操作类型分组的统计
        assert "test_action" in statistics["by_action_type"], \
            "统计应该包含test_action操作类型"
        
        # 获取使用历史
        history = usage_service.get_usage_history(user_id=user.id, limit=50)
        
        # 验证使用历史
        assert len(history) >= 1, "使用历史应该至少有1条记录"
        assert history[0]["action_type"] == "test_action", \
            "最新的使用记录应该是test_action"
        assert abs(history[0]["duration_minutes"] - usage_duration) < 0.01, \
            f"使用记录的时长应该是{usage_duration}"
        
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
    password=password_strategy,
    deduct_duration=st.floats(min_value=0.1, max_value=5.0),
    restore_duration=st.floats(min_value=0.1, max_value=5.0)
)
@settings(max_examples=100)
def test_quota_deduction_and_restoration_property(
    db_session: Session,
    email: str,
    password: str,
    deduct_duration: float,
    restore_duration: float
):
    """
    属性：额度扣减和恢复
    
    对于任意额度扣减和恢复操作，系统应该正确更新用户额度
    
    **验证：需求7.7, 6.8**
    """
    auth_service = AuthenticationService(db_session)
    usage_service = UsageService(db_session)
    
    try:
        # 注册用户
        user = auth_service.register_user(email, password)
        initial_quota = user.remaining_quota_minutes
        
        # 确保有足够的额度进行扣减
        assume(initial_quota >= deduct_duration)
        
        # 扣减额度
        user_after_deduct, cost = usage_service.deduct_quota(
            user_id=user.id,
            duration_minutes=deduct_duration
        )
        
        # 验证扣减后的额度
        expected_after_deduct = initial_quota - deduct_duration
        assert abs(user_after_deduct.remaining_quota_minutes - expected_after_deduct) < 0.01, \
            f"扣减后额度应该是{expected_after_deduct}"
        
        # 恢复额度
        user_after_restore = usage_service.restore_quota(
            user_id=user.id,
            duration_minutes=restore_duration
        )
        
        # 验证恢复后的额度
        expected_after_restore = expected_after_deduct + restore_duration
        assert abs(user_after_restore.remaining_quota_minutes - expected_after_restore) < 0.01, \
            f"恢复后额度应该是{expected_after_restore}"
        
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
    password=password_strategy,
    video_duration=st.floats(min_value=0.1, max_value=10.0)
)
@settings(max_examples=100)
def test_export_cost_calculation_property(
    db_session: Session,
    email: str,
    password: str,
    video_duration: float
):
    """
    属性：导出费用计算
    
    对于任意视频时长，系统应该正确计算导出费用
    
    **验证：需求6.3, 6.5, 6.6**
    """
    auth_service = AuthenticationService(db_session)
    usage_service = UsageService(db_session)
    
    try:
        # 注册用户
        user = auth_service.register_user(email, password)
        initial_quota = user.remaining_quota_minutes
        
        # 计算导出费用
        cost_info = usage_service.calculate_export_cost(
            user_id=user.id,
            video_duration_minutes=video_duration
        )
        
        # 验证费用信息包含必要字段
        assert "user_id" in cost_info, "费用信息应该包含用户ID"
        assert "subscription_tier" in cost_info, "费用信息应该包含订阅层级"
        assert "video_duration_minutes" in cost_info, "费用信息应该包含视频时长"
        assert "remaining_quota_minutes" in cost_info, "费用信息应该包含剩余额度"
        assert "quota_after_export" in cost_info, "费用信息应该包含导出后额度"
        assert "cost" in cost_info, "费用信息应该包含费用"
        assert "needs_payment" in cost_info, "费用信息应该包含是否需要付费"
        assert "message" in cost_info, "费用信息应该包含提示消息"
        
        # 验证费用计算逻辑
        if initial_quota >= video_duration:
            # 额度充足，无需付费
            assert cost_info["cost"] == 0.0, "额度充足时费用应该为0"
            assert cost_info["needs_payment"] is False, "额度充足时不需要付费"
            assert abs(cost_info["quota_after_export"] - (initial_quota - video_duration)) < 0.01, \
                "导出后额度应该正确计算"
        else:
            # 额度不足
            if user.subscription_tier == SubscriptionTier.PAY_PER_USE:
                # 按量付费
                expected_cost = video_duration * usage_service.PAY_PER_USE_PRICE
                assert abs(cost_info["cost"] - expected_cost) < 0.01, \
                    f"按量付费费用应该是{expected_cost}"
                assert cost_info["needs_payment"] is True, "按量付费需要付费"
            else:
                # 订阅制用户
                shortage = video_duration - initial_quota
                expected_cost = shortage * usage_service.PAY_PER_USE_PRICE
                assert abs(cost_info["cost"] - expected_cost) < 0.01, \
                    f"超额费用应该是{expected_cost}"
                assert cost_info["needs_payment"] is True, "超额使用需要付费"
        
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
    password=password_strategy,
    usage_count=st.integers(min_value=1, max_value=10),
    usage_duration=st.floats(min_value=0.1, max_value=2.0)
)
@settings(max_examples=50)
def test_usage_statistics_accuracy_property(
    db_session: Session,
    email: str,
    password: str,
    usage_count: int,
    usage_duration: float
):
    """
    属性：使用统计准确性
    
    对于任意多次使用，系统应该准确统计总使用时长和次数
    
    **验证：需求7.7**
    """
    auth_service = AuthenticationService(db_session)
    usage_service = UsageService(db_session)
    subscription_service = SubscriptionService(db_session)
    
    try:
        # 注册用户并激活专业版（确保有足够额度）
        user = auth_service.register_user(email, password)
        subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        
        db_session.refresh(user)
        
        # 确保有足够的额度
        total_usage = usage_count * usage_duration
        assume(user.remaining_quota_minutes >= total_usage)
        
        # 多次扣减额度
        for i in range(usage_count):
            usage_service.deduct_quota(
                user_id=user.id,
                duration_minutes=usage_duration,
                action_type=f"action_{i % 3}"  # 使用3种不同的操作类型
            )
        
        # 获取使用统计
        statistics = usage_service.get_usage_statistics(
            user_id=user.id,
            days=30
        )
        
        # 验证统计准确性
        assert statistics["usage_count"] >= usage_count, \
            f"使用次数应该至少为{usage_count}"
        assert statistics["total_usage_minutes"] >= total_usage - 0.01, \
            f"总使用时长应该至少为{total_usage}"
        
        # 验证按操作类型分组的统计
        action_types = statistics["by_action_type"]
        total_by_action = sum(action["count"] for action in action_types.values())
        assert total_by_action >= usage_count, \
            "按操作类型统计的总次数应该等于总使用次数"
        
        # 清理
        subscriptions = subscription_service.get_user_subscriptions(user.id)
        for sub in subscriptions:
            db_session.delete(sub)
        db_session.delete(user)
        db_session.commit()
        
    except ValueError as e:
        if "邮箱已被注册" in str(e):
            pytest.skip("邮箱已存在，跳过测试")
        raise
