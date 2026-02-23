"""计费管理服务单元测试"""
import pytest
from datetime import datetime, timedelta
import uuid

from app.services.billing import BillingService
from app.models.user import User, SubscriptionTier
from tests.factories import UserFactory


class TestBillingService:
    """计费管理服务测试类"""
    
    def test_calculate_export_cost_free_tier_sufficient_quota(self, db_session):
        """测试免费版用户配额充足时的费用计算"""
        # 创建免费版用户，剩余5分钟配额
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.FREE,
            remaining_quota_minutes=5.0
        )
        
        billing_service = BillingService(db_session)
        
        # 导出3分钟视频
        result = billing_service.calculate_export_cost(
            user_id=user.id,
            video_duration_minutes=3.0
        )
        
        assert result["subscription_tier"] == "FREE"
        assert result["video_duration_minutes"] == 3.0
        assert result["remaining_quota"] == 5.0
        assert result["quota_used"] == 3.0
        assert result["overage_minutes"] == 0.0
        assert result["base_cost"] == 0.0
        assert result["overage_cost"] == 0.0
        assert result["total_cost"] == 0.0
        assert result["needs_payment"] is False
    
    def test_calculate_export_cost_free_tier_insufficient_quota(self, db_session):
        """测试免费版用户配额不足时抛出异常"""
        # 创建免费版用户，剩余2分钟配额
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.FREE,
            remaining_quota_minutes=2.0
        )
        
        billing_service = BillingService(db_session)
        
        # 尝试导出5分钟视频，应该抛出异常
        with pytest.raises(ValueError, match="免费版额度不足"):
            billing_service.calculate_export_cost(
                user_id=user.id,
                video_duration_minutes=5.0
            )
    
    def test_calculate_export_cost_pay_per_use(self, db_session):
        """测试按量付费用户的费用计算"""
        # 创建按量付费用户
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PAY_PER_USE,
            remaining_quota_minutes=0.0
        )
        
        billing_service = BillingService(db_session)
        
        # 导出3分钟视频
        result = billing_service.calculate_export_cost(
            user_id=user.id,
            video_duration_minutes=3.0
        )
        
        assert result["subscription_tier"] == "PAY_PER_USE"
        assert result["video_duration_minutes"] == 3.0
        assert result["quota_used"] == 0.0
        assert result["overage_minutes"] == 0.0
        assert result["base_cost"] == 30.0  # 3分钟 × ¥10/分钟
        assert result["overage_cost"] == 0.0
        assert result["total_cost"] == 30.0
        assert result["needs_payment"] is True
    
    def test_calculate_export_cost_professional_sufficient_quota(self, db_session):
        """测试专业版用户配额充足时的费用计算"""
        # 创建专业版用户，剩余50分钟配额
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=50.0
        )
        
        billing_service = BillingService(db_session)
        
        # 导出30分钟视频
        result = billing_service.calculate_export_cost(
            user_id=user.id,
            video_duration_minutes=30.0
        )
        
        assert result["subscription_tier"] == "PROFESSIONAL"
        assert result["video_duration_minutes"] == 30.0
        assert result["remaining_quota"] == 50.0
        assert result["quota_used"] == 30.0
        assert result["overage_minutes"] == 0.0
        assert result["base_cost"] == 0.0
        assert result["overage_cost"] == 0.0
        assert result["total_cost"] == 0.0
        assert result["needs_payment"] is False
    
    def test_calculate_export_cost_professional_with_overage(self, db_session):
        """测试专业版用户超额使用时的费用计算"""
        # 创建专业版用户，剩余30分钟配额
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=30.0
        )
        
        billing_service = BillingService(db_session)
        
        # 导出40分钟视频（超出10分钟）
        result = billing_service.calculate_export_cost(
            user_id=user.id,
            video_duration_minutes=40.0
        )
        
        assert result["subscription_tier"] == "PROFESSIONAL"
        assert result["video_duration_minutes"] == 40.0
        assert result["remaining_quota"] == 30.0
        assert result["quota_used"] == 30.0
        assert result["overage_minutes"] == 10.0
        assert result["base_cost"] == 0.0
        assert result["overage_cost"] == 120.0  # 10分钟 × ¥12/分钟
        assert result["total_cost"] == 120.0
        assert result["needs_payment"] is True
    
    def test_calculate_export_cost_enterprise_with_overage(self, db_session):
        """测试企业版用户超额使用时的费用计算"""
        # 创建企业版用户，剩余100分钟配额
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.ENTERPRISE,
            remaining_quota_minutes=100.0
        )
        
        billing_service = BillingService(db_session)
        
        # 导出120分钟视频（超出20分钟）
        result = billing_service.calculate_export_cost(
            user_id=user.id,
            video_duration_minutes=120.0
        )
        
        assert result["subscription_tier"] == "ENTERPRISE"
        assert result["video_duration_minutes"] == 120.0
        assert result["remaining_quota"] == 100.0
        assert result["quota_used"] == 100.0
        assert result["overage_minutes"] == 20.0
        assert result["base_cost"] == 0.0
        assert result["overage_cost"] == 200.0  # 20分钟 × ¥10/分钟（企业版优惠）
        assert result["total_cost"] == 200.0
        assert result["needs_payment"] is True
    
    def test_calculate_export_cost_invalid_duration(self, db_session):
        """测试无效的视频时长"""
        user = UserFactory.create(db_session)
        billing_service = BillingService(db_session)
        
        with pytest.raises(ValueError, match="视频时长必须大于0"):
            billing_service.calculate_export_cost(
                user_id=user.id,
                video_duration_minutes=0.0
            )
        
        with pytest.raises(ValueError, match="视频时长必须大于0"):
            billing_service.calculate_export_cost(
                user_id=user.id,
                video_duration_minutes=-5.0
            )
    
    def test_calculate_export_cost_user_not_found(self, db_session):
        """测试用户不存在的情况"""
        billing_service = BillingService(db_session)
        
        with pytest.raises(ValueError, match="用户不存在"):
            billing_service.calculate_export_cost(
                user_id=uuid.uuid4(),
                video_duration_minutes=5.0
            )
    
    def test_calculate_overage_cost_pay_per_use(self, db_session):
        """测试按量付费用户的超额费用计算"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PAY_PER_USE
        )
        
        billing_service = BillingService(db_session)
        
        # 计算10分钟超额费用
        cost = billing_service.calculate_overage_cost(
            user_id=user.id,
            overage_minutes=10.0
        )
        
        assert cost == 100.0  # 10分钟 × ¥10/分钟
    
    def test_calculate_overage_cost_professional(self, db_session):
        """测试专业版用户的超额费用计算"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL
        )
        
        billing_service = BillingService(db_session)
        
        # 计算5分钟超额费用
        cost = billing_service.calculate_overage_cost(
            user_id=user.id,
            overage_minutes=5.0
        )
        
        assert cost == 60.0  # 5分钟 × ¥12/分钟
    
    def test_calculate_overage_cost_free_tier_not_allowed(self, db_session):
        """测试免费版用户不允许超额"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.FREE
        )
        
        billing_service = BillingService(db_session)
        
        with pytest.raises(ValueError, match="不允许超额使用"):
            billing_service.calculate_overage_cost(
                user_id=user.id,
                overage_minutes=5.0
            )
    
    def test_get_subscription_quota(self, db_session):
        """测试获取订阅计划配额"""
        billing_service = BillingService(db_session)
        
        assert billing_service.get_subscription_quota(SubscriptionTier.FREE) == 5.0
        assert billing_service.get_subscription_quota(SubscriptionTier.PAY_PER_USE) == 0.0
        assert billing_service.get_subscription_quota(SubscriptionTier.PROFESSIONAL) == 50.0
        assert billing_service.get_subscription_quota(SubscriptionTier.ENTERPRISE) == 200.0
    
    def test_check_quota_availability_sufficient(self, db_session):
        """测试配额充足的情况"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=50.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.check_quota_availability(
            user_id=user.id,
            required_minutes=30.0
        )
        
        assert result["remaining_quota"] == 50.0
        assert result["required_minutes"] == 30.0
        assert result["is_sufficient"] is True
        assert result["shortage"] == 0.0
        assert result["overage_allowed"] is True
        assert result["can_proceed"] is True
    
    def test_check_quota_availability_insufficient_with_overage(self, db_session):
        """测试配额不足但允许超额的情况"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=20.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.check_quota_availability(
            user_id=user.id,
            required_minutes=30.0
        )
        
        assert result["remaining_quota"] == 20.0
        assert result["required_minutes"] == 30.0
        assert result["is_sufficient"] is False
        assert result["shortage"] == 10.0
        assert result["overage_allowed"] is True
        assert result["can_proceed"] is True
    
    def test_check_quota_availability_insufficient_no_overage(self, db_session):
        """测试配额不足且不允许超额的情况"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.FREE,
            remaining_quota_minutes=2.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.check_quota_availability(
            user_id=user.id,
            required_minutes=5.0
        )
        
        assert result["remaining_quota"] == 2.0
        assert result["required_minutes"] == 5.0
        assert result["is_sufficient"] is False
        assert result["shortage"] == 3.0
        assert result["overage_allowed"] is False
        assert result["can_proceed"] is False
    
    def test_estimate_monthly_cost_free_tier(self, db_session):
        """测试免费版月度费用预估"""
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_monthly_cost(
            subscription_tier=SubscriptionTier.FREE,
            estimated_usage_minutes=5.0
        )
        
        assert result["subscription_tier"] == "FREE"
        assert result["monthly_price"] == 0.0
        assert result["monthly_quota"] == 5.0
        assert result["estimated_usage_minutes"] == 5.0
        assert result["overage_minutes"] == 0.0
        assert result["overage_cost"] == 0.0
        assert result["total_cost"] == 0.0
    
    def test_estimate_monthly_cost_pay_per_use(self, db_session):
        """测试按量付费月度费用预估"""
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_monthly_cost(
            subscription_tier=SubscriptionTier.PAY_PER_USE,
            estimated_usage_minutes=20.0
        )
        
        assert result["subscription_tier"] == "PAY_PER_USE"
        assert result["monthly_price"] == 0.0
        assert result["monthly_quota"] == 0.0
        assert result["estimated_usage_minutes"] == 20.0
        assert result["overage_minutes"] == 0.0
        assert result["overage_cost"] == 0.0
        assert result["total_cost"] == 200.0  # 20分钟 × ¥10/分钟
    
    def test_estimate_monthly_cost_professional_no_overage(self, db_session):
        """测试专业版月度费用预估（无超额）"""
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_monthly_cost(
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            estimated_usage_minutes=40.0
        )
        
        assert result["subscription_tier"] == "PROFESSIONAL"
        assert result["monthly_price"] == 299.0
        assert result["monthly_quota"] == 50.0
        assert result["estimated_usage_minutes"] == 40.0
        assert result["overage_minutes"] == 0.0
        assert result["overage_cost"] == 0.0
        assert result["total_cost"] == 299.0
    
    def test_estimate_monthly_cost_professional_with_overage(self, db_session):
        """测试专业版月度费用预估（有超额）"""
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_monthly_cost(
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            estimated_usage_minutes=60.0
        )
        
        assert result["subscription_tier"] == "PROFESSIONAL"
        assert result["monthly_price"] == 299.0
        assert result["monthly_quota"] == 50.0
        assert result["estimated_usage_minutes"] == 60.0
        assert result["overage_minutes"] == 10.0
        assert result["overage_cost"] == 120.0  # 10分钟 × ¥12/分钟
        assert result["total_cost"] == 419.0  # 299 + 120
    
    def test_estimate_monthly_cost_enterprise_with_overage(self, db_session):
        """测试企业版月度费用预估（有超额）"""
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_monthly_cost(
            subscription_tier=SubscriptionTier.ENTERPRISE,
            estimated_usage_minutes=250.0
        )
        
        assert result["subscription_tier"] == "ENTERPRISE"
        assert result["monthly_price"] == 999.0
        assert result["monthly_quota"] == 200.0
        assert result["estimated_usage_minutes"] == 250.0
        assert result["overage_minutes"] == 50.0
        assert result["overage_cost"] == 500.0  # 50分钟 × ¥10/分钟
        assert result["total_cost"] == 1499.0  # 999 + 500
    
    def test_get_pricing_plans(self, db_session):
        """测试获取定价计划"""
        billing_service = BillingService(db_session)
        
        plans = billing_service.get_pricing_plans()
        
        assert len(plans) == 4
        
        # 验证每个计划都有必要的字段
        for plan in plans:
            assert "tier" in plan
            assert "name" in plan
            assert "monthly_price" in plan
            assert "monthly_quota" in plan
            assert "overage_allowed" in plan
        
        # 验证免费版
        free_plan = next(p for p in plans if p["tier"] == "FREE")
        assert free_plan["monthly_price"] == 0.0
        assert free_plan["monthly_quota"] == 5.0
        assert free_plan["overage_allowed"] is False
        
        # 验证专业版
        pro_plan = next(p for p in plans if p["tier"] == "PROFESSIONAL")
        assert pro_plan["monthly_price"] == 299.0
        assert pro_plan["monthly_quota"] == 50.0
        assert pro_plan["overage_allowed"] is True


    def test_estimate_export_cost_with_details_sufficient_quota(self, db_session):
        """测试费用预估（配额充足）"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=50.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_export_cost_with_details(
            user_id=user.id,
            video_duration_minutes=30.0
        )
        
        assert result["user_id"] == str(user.id)
        assert result["subscription_tier"] == "PROFESSIONAL"
        assert result["video_duration_minutes"] == 30.0
        assert result["current_quota"] == 50.0
        assert result["quota_after_export"] == 20.0
        assert result["cost_breakdown"]["quota_used"] == 30.0
        assert result["cost_breakdown"]["total_cost"] == 0.0
        assert result["needs_payment"] is False
        assert result["can_proceed"] is True
        assert "无需额外支付" in result["recommendation"]
    
    def test_estimate_export_cost_with_details_with_overage(self, db_session):
        """测试费用预估（需要超额）"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=20.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_export_cost_with_details(
            user_id=user.id,
            video_duration_minutes=30.0
        )
        
        assert result["current_quota"] == 20.0
        assert result["quota_after_export"] == 0.0
        assert result["cost_breakdown"]["quota_used"] == 20.0
        assert result["cost_breakdown"]["overage_minutes"] == 10.0
        assert result["cost_breakdown"]["overage_cost"] == 120.0
        assert result["cost_breakdown"]["total_cost"] == 120.0
        assert result["needs_payment"] is True
        assert result["can_proceed"] is True
        assert "超额使用需支付" in result["recommendation"]
    
    def test_estimate_export_cost_with_details_pay_per_use(self, db_session):
        """测试费用预估（按量付费）"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PAY_PER_USE,
            remaining_quota_minutes=0.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.estimate_export_cost_with_details(
            user_id=user.id,
            video_duration_minutes=15.0
        )
        
        assert result["subscription_tier"] == "PAY_PER_USE"
        assert result["cost_breakdown"]["base_cost"] == 150.0
        assert result["cost_breakdown"]["total_cost"] == 150.0
        assert result["needs_payment"] is True
        assert result["can_proceed"] is True
        assert "按量付费模式" in result["recommendation"]
    
    def test_estimate_export_cost_with_details_free_tier_insufficient(self, db_session):
        """测试费用预估（免费版配额不足）"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.FREE,
            remaining_quota_minutes=2.0
        )
        
        billing_service = BillingService(db_session)
        
        # 免费版配额不足会抛出异常
        with pytest.raises(ValueError, match="免费版额度不足"):
            billing_service.estimate_export_cost_with_details(
                user_id=user.id,
                video_duration_minutes=5.0
            )
    
    def test_confirm_export_with_cost_user_confirmed(self, db_session):
        """测试导出确认（用户已确认）"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=50.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.confirm_export_with_cost(
            user_id=user.id,
            video_duration_minutes=30.0,
            user_confirmed=True
        )
        
        assert result["confirmed"] is True
        assert result["can_proceed"] is True
        assert "费用已确认" in result["message"]
        assert "estimate" in result
        assert result["estimate"]["video_duration_minutes"] == 30.0
    
    def test_confirm_export_with_cost_user_not_confirmed(self, db_session):
        """测试导出确认（用户未确认）"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=50.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.confirm_export_with_cost(
            user_id=user.id,
            video_duration_minutes=30.0,
            user_confirmed=False
        )
        
        assert result["confirmed"] is False
        assert result["can_proceed"] is False
        assert "用户未确认费用" in result["message"]
    
    def test_confirm_export_with_cost_insufficient_quota_no_overage(self, db_session):
        """测试导出确认（配额不足且不允许超额）"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.FREE,
            remaining_quota_minutes=2.0
        )
        
        billing_service = BillingService(db_session)
        
        # 免费版配额不足会抛出异常
        with pytest.raises(ValueError, match="免费版额度不足"):
            billing_service.confirm_export_with_cost(
                user_id=user.id,
                video_duration_minutes=5.0,
                user_confirmed=True
            )
    
    def test_confirm_export_with_cost_with_payment(self, db_session):
        """测试导出确认（需要支付）"""
        user = UserFactory.create(
            db_session,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=10.0
        )
        
        billing_service = BillingService(db_session)
        
        result = billing_service.confirm_export_with_cost(
            user_id=user.id,
            video_duration_minutes=20.0,
            user_confirmed=True
        )
        
        assert result["confirmed"] is True
        assert result["can_proceed"] is True
        assert result["estimate"]["needs_payment"] is True
        assert result["estimate"]["cost_breakdown"]["overage_cost"] > 0
