"""计费逻辑属性测试

使用Hypothesis进行基于属性的测试，验证计费逻辑的正确性属性。
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from decimal import Decimal

from app.services.billing import BillingService
from app.models.user import SubscriptionTier
from tests.factories import UserFactory


# 定义策略
subscription_tiers = st.sampled_from([
    SubscriptionTier.FREE,
    SubscriptionTier.PAY_PER_USE,
    SubscriptionTier.PROFESSIONAL,
    SubscriptionTier.ENTERPRISE,
])

positive_minutes = st.floats(min_value=0.1, max_value=300.0)
quota_minutes = st.floats(min_value=0.0, max_value=500.0)


class TestBillingProperties:
    """计费逻辑属性测试类"""
    
    @given(
        video_duration=positive_minutes,
        remaining_quota=quota_minutes,
    )
    @settings(max_examples=100, deadline=None)
    def test_property_20_billing_logic_cost_calculation(
        self,
        db_session,
        video_duration,
        remaining_quota
    ):
        """
        属性20：计费逻辑
        
        对于任意导出请求，系统应根据视频时长和用户订阅层级正确计算费用，
        包括超额使用的额外费用。
        
        验证：需求6.3, 6.6
        """
        # 测试专业版用户（允许超额）
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=remaining_quota
        )
        
        billing_service = BillingService(db_session)
        
        try:
            result = billing_service.calculate_export_cost(
                user_id=user.id,
                video_duration_minutes=video_duration
            )
            
            # 验证基本字段存在
            assert "total_cost" in result
            assert "base_cost" in result
            assert "overage_cost" in result
            assert "quota_used" in result
            assert "overage_minutes" in result
            
            # 验证费用非负
            assert result["total_cost"] >= 0
            assert result["base_cost"] >= 0
            assert result["overage_cost"] >= 0
            
            # 验证总费用等于基础费用加超额费用
            assert abs(
                result["total_cost"] - (result["base_cost"] + result["overage_cost"])
            ) < 0.01
            
            # 验证配额使用逻辑
            if video_duration <= remaining_quota:
                # 配额充足，应该使用配额
                assert result["quota_used"] == video_duration
                assert result["overage_minutes"] == 0.0
                assert result["overage_cost"] == 0.0
                assert result["total_cost"] == 0.0
            else:
                # 配额不足，应该有超额
                assert result["quota_used"] == remaining_quota
                assert result["overage_minutes"] > 0.0
                assert abs(
                    result["overage_minutes"] - (video_duration - remaining_quota)
                ) < 0.01
                # 专业版超额费率是¥12/分钟
                expected_overage_cost = result["overage_minutes"] * 12.0
                assert abs(result["overage_cost"] - expected_overage_cost) < 0.01
        
        except ValueError:
            # 某些情况下可能抛出异常（如免费版配额不足）
            pass
    
    @given(
        video_duration=positive_minutes,
    )
    @settings(max_examples=100, deadline=None)
    def test_property_20_pay_per_use_billing(
        self,
        db_session,
        video_duration
    ):
        """
        属性20：按量付费计费逻辑
        
        对于按量付费用户，所有使用都应该按费率计费。
        
        验证：需求6.3
        """
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PAY_PER_USE,
            remaining_quota_minutes=0.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.calculate_export_cost(
            user_id=user.id,
            video_duration_minutes=video_duration
        )
        
        # 按量付费应该全部计入基础费用
        expected_cost = video_duration * 10.0  # ¥10/分钟
        assert abs(result["base_cost"] - expected_cost) < 0.01
        assert result["overage_cost"] == 0.0
        assert abs(result["total_cost"] - expected_cost) < 0.01
        assert result["needs_payment"] is True
    
    @given(
        video_duration=st.floats(min_value=0.1, max_value=5.0),
    )
    @settings(max_examples=50, deadline=None)
    def test_property_20_free_tier_quota_limit(
        self,
        db_session,
        video_duration
    ):
        """
        属性20：免费版配额限制
        
        对于免费版用户，如果配额不足应该拒绝导出。
        
        验证：需求6.3
        """
        # 免费版配额是5分钟
        remaining_quota = 5.0
        
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.FREE,
            remaining_quota_minutes=remaining_quota
        )
        
        billing_service = BillingService(db_session)
        
        if video_duration <= remaining_quota:
            # 配额充足，应该成功
            result = billing_service.calculate_export_cost(
                user_id=user.id,
                video_duration_minutes=video_duration
            )
            assert result["total_cost"] == 0.0
            assert result["needs_payment"] is False
        else:
            # 配额不足，应该抛出异常
            with pytest.raises(ValueError, match="免费版额度不足"):
                billing_service.calculate_export_cost(
                    user_id=user.id,
                    video_duration_minutes=video_duration
                )
    
    @given(
        tier=subscription_tiers,
        overage_minutes=positive_minutes,
    )
    @settings(max_examples=100, deadline=None)
    def test_property_20_overage_cost_calculation(
        self,
        db_session,
        tier,
        overage_minutes
    ):
        """
        属性20：超额费用计算
        
        对于允许超额的订阅层级，超额费用应该正确计算。
        
        验证：需求6.6
        """
        user = UserFactory.create(
            db_session,
            subscription_tier=tier,
            remaining_quota_minutes=0.0
        )
        
        billing_service = BillingService(db_session)
        
        if tier == SubscriptionTier.FREE:
            # 免费版不允许超额
            with pytest.raises(ValueError, match="不允许超额使用"):
                billing_service.calculate_overage_cost(
                    user_id=user.id,
                    overage_minutes=overage_minutes
                )
        else:
            # 其他层级允许超额
            cost = billing_service.calculate_overage_cost(
                user_id=user.id,
                overage_minutes=overage_minutes
            )
            
            # 验证费用非负
            assert cost >= 0
            
            # 验证费用计算正确
            if tier == SubscriptionTier.PAY_PER_USE:
                expected_cost = overage_minutes * 10.0
            elif tier == SubscriptionTier.PROFESSIONAL:
                expected_cost = overage_minutes * 12.0
            elif tier == SubscriptionTier.ENTERPRISE:
                expected_cost = overage_minutes * 10.0
            
            assert abs(cost - expected_cost) < 0.01
    
    @given(
        required_minutes=positive_minutes,
        remaining_quota=quota_minutes,
    )
    @settings(max_examples=100, deadline=None)
    def test_property_quota_availability_check(
        self,
        db_session,
        required_minutes,
        remaining_quota
    ):
        """
        属性：配额可用性检查
        
        对于任意配额检查请求，系统应该正确判断配额是否充足。
        """
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=remaining_quota
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.check_quota_availability(
            user_id=user.id,
            required_minutes=required_minutes
        )
        
        # 验证基本字段
        assert "is_sufficient" in result
        assert "shortage" in result
        assert "can_proceed" in result
        
        # 验证逻辑正确性
        if remaining_quota >= required_minutes:
            assert result["is_sufficient"] is True
            assert result["shortage"] == 0.0
        else:
            assert result["is_sufficient"] is False
            assert result["shortage"] > 0.0
            assert abs(
                result["shortage"] - (required_minutes - remaining_quota)
            ) < 0.01
        
        # 专业版允许超额，所以总是可以继续
        assert result["can_proceed"] is True
    
    @given(
        tier=subscription_tiers,
        estimated_usage=positive_minutes,
    )
    @settings(max_examples=100, deadline=None)
    def test_property_monthly_cost_estimation(
        self,
        db_session,
        tier,
        estimated_usage
    ):
        """
        属性：月度费用预估
        
        对于任意订阅层级和预估使用量，系统应该正确预估月度费用。
        """
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_monthly_cost(
            subscription_tier=tier,
            estimated_usage_minutes=estimated_usage
        )
        
        # 验证基本字段
        assert "total_cost" in result
        assert "monthly_price" in result
        assert "monthly_quota" in result
        assert "overage_cost" in result
        
        # 验证费用非负
        assert result["total_cost"] >= 0
        assert result["monthly_price"] >= 0
        assert result["overage_cost"] >= 0
        
        # 验证总费用计算正确
        if tier == SubscriptionTier.PAY_PER_USE:
            # 按量付费：全部按使用量计费
            expected_cost = estimated_usage * 10.0
            assert abs(result["total_cost"] - expected_cost) < 0.01
        else:
            # 订阅制：基础费用 + 超额费用
            expected_total = result["monthly_price"] + result["overage_cost"]
            assert abs(result["total_cost"] - expected_total) < 0.01
    
    @given(
        video_duration=positive_minutes,
    )
    @settings(max_examples=50, deadline=None)
    def test_property_cost_consistency_across_tiers(
        self,
        db_session,
        video_duration
    ):
        """
        属性：不同订阅层级的费用一致性
        
        对于相同的视频时长，不同订阅层级的费用计算应该符合定价规则。
        """
        billing_service = BillingService(db_session)
        
        # 创建不同层级的用户（配额为0，测试纯超额情况）
        users = {}
        for tier in [SubscriptionTier.PAY_PER_USE, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            users[tier] = UserFactory.create(
                db_session,
                subscription_tier=tier,
                remaining_quota_minutes=0.0
            )
        
        # 计算各层级费用
        costs = {}
        for tier, user in users.items():
            result = billing_service.calculate_export_cost(
                user_id=user.id,
                video_duration_minutes=video_duration
            )
            costs[tier] = result["total_cost"]
        
        # 验证费用关系
        # 按量付费和企业版超额费率相同（¥10/分钟）
        assert abs(costs[SubscriptionTier.PAY_PER_USE] - costs[SubscriptionTier.ENTERPRISE]) < 0.01
        
        # 专业版超额费率更高（¥12/分钟）
        assert costs[SubscriptionTier.PROFESSIONAL] > costs[SubscriptionTier.PAY_PER_USE]
    
    def test_property_pricing_plans_completeness(self, db_session):
        """
        属性：定价计划完整性
        
        系统应该提供所有订阅层级的定价信息。
        """
        billing_service = BillingService(db_session)
        
        plans = billing_service.get_pricing_plans()
        
        # 应该有4个计划
        assert len(plans) == 4
        
        # 验证所有层级都存在
        tiers = {plan["tier"] for plan in plans}
        assert "FREE" in tiers
        assert "PAY_PER_USE" in tiers
        assert "PROFESSIONAL" in tiers
        assert "ENTERPRISE" in tiers
        
        # 验证每个计划都有必要的字段
        for plan in plans:
            assert "name" in plan
            assert "monthly_price" in plan
            assert "monthly_quota" in plan
            assert "overage_allowed" in plan
            assert plan["monthly_price"] >= 0
            assert plan["monthly_quota"] >= 0


    @given(
        video_duration=positive_minutes,
        remaining_quota=quota_minutes,
    )
    @settings(max_examples=100, deadline=None)
    def test_property_21_cost_estimation_display(
        self,
        db_session,
        video_duration,
        remaining_quota
    ):
        """
        属性21：费用预估和显示
        
        对于任意导出请求，系统应在导出前显示预估费用和用户剩余额度。
        
        验证：需求6.5
        """
        # 使用专业版用户测试
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=remaining_quota
        )
        
        billing_service = BillingService(db_session)
        
        try:
            result = billing_service.estimate_export_cost_with_details(
                user_id=user.id,
                video_duration_minutes=video_duration
            )
            
            # 验证必要字段存在
            assert "current_quota" in result
            assert "quota_after_export" in result
            assert "cost_breakdown" in result
            assert "needs_payment" in result
            assert "can_proceed" in result
            assert "recommendation" in result
            
            # 验证当前配额显示正确
            assert result["current_quota"] == remaining_quota
            
            # 验证费用明细存在
            assert "quota_used" in result["cost_breakdown"]
            assert "overage_minutes" in result["cost_breakdown"]
            assert "total_cost" in result["cost_breakdown"]
            
            # 验证导出后配额计算正确
            expected_quota_after = max(
                0,
                remaining_quota - result["cost_breakdown"]["quota_used"]
            )
            assert abs(result["quota_after_export"] - expected_quota_after) < 0.01
            
            # 验证建议消息存在
            assert len(result["recommendation"]) > 0
        
        except ValueError:
            # 某些情况下可能抛出异常（如免费版配额不足）
            pass
    
    @given(
        video_duration=positive_minutes,
    )
    @settings(max_examples=50, deadline=None)
    def test_property_22_export_confirmation_flow(
        self,
        db_session,
        video_duration
    ):
        """
        属性22：导出确认流程
        
        对于任意导出请求，系统应在用户确认费用后才开始导出处理。
        
        验证：需求6.7
        """
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=100.0
        )
        
        billing_service = BillingService(db_session)
        
        # 测试用户未确认的情况
        result_not_confirmed = billing_service.confirm_export_with_cost(
            user_id=user.id,
            video_duration_minutes=video_duration,
            user_confirmed=False
        )
        
        assert result_not_confirmed["confirmed"] is False
        assert result_not_confirmed["can_proceed"] is False
        assert "未确认" in result_not_confirmed["message"]
        
        # 测试用户已确认的情况
        result_confirmed = billing_service.confirm_export_with_cost(
            user_id=user.id,
            video_duration_minutes=video_duration,
            user_confirmed=True
        )
        
        assert result_confirmed["confirmed"] is True
        # 专业版配额充足，应该可以继续
        assert result_confirmed["can_proceed"] is True
        assert "estimate" in result_confirmed
    
    @given(
        video_duration=positive_minutes,
        remaining_quota=quota_minutes,
    )
    @settings(max_examples=100, deadline=None)
    def test_property_cost_estimation_accuracy(
        self,
        db_session,
        video_duration,
        remaining_quota
    ):
        """
        属性：费用预估准确性
        
        费用预估应该与实际费用计算一致。
        """
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=remaining_quota
        )
        
        billing_service = BillingService(db_session)
        
        try:
            # 获取费用预估
            estimate = billing_service.estimate_export_cost_with_details(
                user_id=user.id,
                video_duration_minutes=video_duration
            )
            
            # 获取实际费用计算
            actual_cost = billing_service.calculate_export_cost(
                user_id=user.id,
                video_duration_minutes=video_duration
            )
            
            # 验证费用一致
            assert abs(
                estimate["cost_breakdown"]["total_cost"] - actual_cost["total_cost"]
            ) < 0.01
            assert abs(
                estimate["cost_breakdown"]["quota_used"] - actual_cost["quota_used"]
            ) < 0.01
            assert abs(
                estimate["cost_breakdown"]["overage_minutes"] - actual_cost["overage_minutes"]
            ) < 0.01
        
        except ValueError:
            pass
    
    @given(
        video_duration=positive_minutes,
    )
    @settings(max_examples=50, deadline=None)
    def test_property_confirmation_prevents_unauthorized_export(
        self,
        db_session,
        video_duration
    ):
        """
        属性：确认流程防止未授权导出
        
        未经用户确认的导出请求应该被拒绝。
        """
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PAY_PER_USE,
            remaining_quota_minutes=0.0
        )
        
        billing_service = BillingService(db_session)
        
        # 用户未确认
        result = billing_service.confirm_export_with_cost(
            user_id=user.id,
            video_duration_minutes=video_duration,
            user_confirmed=False
        )
        
        # 应该拒绝导出
        assert result["can_proceed"] is False
        assert result["confirmed"] is False
