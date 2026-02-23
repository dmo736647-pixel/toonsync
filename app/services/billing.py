"""计费管理服务

本模块实现计费管理功能，包括：
- 按量计费算法
- 超额计费算法
- 订阅配额管理
- 费用预估和确认流程
"""
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
import uuid

from app.models.user import User, SubscriptionTier
from app.models.subscription import Subscription


class BillingService:
    """计费管理服务类
    
    负责处理所有与计费相关的业务逻辑，包括费用计算、配额管理和费用预估。
    """
    
    # 定价配置
    PRICING_CONFIG = {
        # 按量付费价格（¥/分钟）
        "pay_per_use_rate": 10.0,
        
        # 超额使用价格（¥/分钟）- 订阅用户超出配额后的价格
        "overage_rate": 12.0,
        
        # 订阅计划配置
        "subscription_plans": {
            SubscriptionTier.FREE: {
                "name": "基础版（免费）",
                "monthly_quota": 5.0,  # 分钟
                "monthly_price": 0.0,
                "overage_allowed": False,  # 不允许超额
            },
            SubscriptionTier.PAY_PER_USE: {
                "name": "按量付费",
                "monthly_quota": 0.0,  # 无固定配额
                "monthly_price": 0.0,
                "overage_allowed": True,
                "rate": 10.0,  # ¥/分钟
            },
            SubscriptionTier.PROFESSIONAL: {
                "name": "专业版",
                "monthly_quota": 50.0,  # 分钟
                "monthly_price": 299.0,
                "overage_allowed": True,
                "overage_rate": 12.0,  # ¥/分钟
            },
            SubscriptionTier.ENTERPRISE: {
                "name": "企业版",
                "monthly_quota": 200.0,  # 分钟
                "monthly_price": 999.0,
                "overage_allowed": True,
                "overage_rate": 10.0,  # ¥/分钟（企业版优惠）
            },
        }
    }
    
    def __init__(self, db: Session):
        """初始化计费服务
        
        参数:
            db: 数据库会话
        """
        self.db = db
    
    def calculate_export_cost(
        self,
        user_id: uuid.UUID,
        video_duration_minutes: float
    ) -> Dict:
        """计算导出费用
        
        根据用户订阅层级和视频时长计算导出费用，包括超额使用的额外费用。
        
        参数:
            user_id: 用户ID
            video_duration_minutes: 视频时长（分钟）
        
        返回:
            Dict: 费用详情，包含：
                - base_cost: 基础费用
                - overage_cost: 超额费用
                - total_cost: 总费用
                - remaining_quota: 剩余配额
                - quota_used: 使用的配额
                - overage_minutes: 超额分钟数
                - needs_payment: 是否需要支付
        
        异常:
            ValueError: 用户不存在或参数无效
        """
        if video_duration_minutes <= 0:
            raise ValueError("视频时长必须大于0")
        
        # 获取用户信息
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 获取订阅计划配置
        plan_config = self.PRICING_CONFIG["subscription_plans"].get(
            user.subscription_tier
        )
        if not plan_config:
            raise ValueError(f"无效的订阅层级: {user.subscription_tier}")
        
        # 计算费用
        remaining_quota = user.remaining_quota_minutes
        base_cost = 0.0
        overage_cost = 0.0
        quota_used = 0.0
        overage_minutes = 0.0
        
        if user.subscription_tier == SubscriptionTier.FREE:
            # 免费版：只能使用配额，不允许超额
            if video_duration_minutes > remaining_quota:
                raise ValueError(
                    f"免费版额度不足。需要{video_duration_minutes}分钟，"
                    f"剩余{remaining_quota}分钟。请升级订阅计划。"
                )
            quota_used = video_duration_minutes
            
        elif user.subscription_tier == SubscriptionTier.PAY_PER_USE:
            # 按量付费：全部按使用量计费
            base_cost = video_duration_minutes * plan_config["rate"]
            
        else:
            # 订阅制（专业版/企业版）：先使用配额，超出部分按超额费率计费
            if video_duration_minutes <= remaining_quota:
                # 配额充足
                quota_used = video_duration_minutes
            else:
                # 配额不足，需要超额付费
                quota_used = remaining_quota
                overage_minutes = video_duration_minutes - remaining_quota
                overage_cost = overage_minutes * plan_config.get(
                    "overage_rate",
                    self.PRICING_CONFIG["overage_rate"]
                )
        
        total_cost = base_cost + overage_cost
        needs_payment = total_cost > 0
        
        return {
            "user_id": str(user_id),
            "subscription_tier": user.subscription_tier.value,
            "video_duration_minutes": video_duration_minutes,
            "remaining_quota": remaining_quota,
            "quota_used": quota_used,
            "overage_minutes": overage_minutes,
            "base_cost": base_cost,
            "overage_cost": overage_cost,
            "total_cost": total_cost,
            "needs_payment": needs_payment,
            "currency": "CNY",
        }
    
    def calculate_overage_cost(
        self,
        user_id: uuid.UUID,
        overage_minutes: float
    ) -> float:
        """计算超额费用
        
        参数:
            user_id: 用户ID
            overage_minutes: 超额分钟数
        
        返回:
            float: 超额费用
        
        异常:
            ValueError: 用户不存在或不允许超额
        """
        if overage_minutes <= 0:
            return 0.0
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        plan_config = self.PRICING_CONFIG["subscription_plans"].get(
            user.subscription_tier
        )
        
        if not plan_config:
            raise ValueError(f"无效的订阅层级: {user.subscription_tier}")
        
        if not plan_config.get("overage_allowed", False):
            raise ValueError(
                f"{plan_config['name']}不允许超额使用，请升级订阅计划"
            )
        
        # 获取超额费率
        if user.subscription_tier == SubscriptionTier.PAY_PER_USE:
            rate = plan_config["rate"]
        else:
            rate = plan_config.get(
                "overage_rate",
                self.PRICING_CONFIG["overage_rate"]
            )
        
        return overage_minutes * rate
    
    def get_subscription_quota(
        self,
        subscription_tier: SubscriptionTier
    ) -> float:
        """获取订阅计划的配额
        
        参数:
            subscription_tier: 订阅层级
        
        返回:
            float: 月度配额（分钟）
        """
        plan_config = self.PRICING_CONFIG["subscription_plans"].get(
            subscription_tier
        )
        if not plan_config:
            raise ValueError(f"无效的订阅层级: {subscription_tier}")
        
        return plan_config["monthly_quota"]
    
    def check_quota_availability(
        self,
        user_id: uuid.UUID,
        required_minutes: float
    ) -> Dict:
        """检查配额可用性
        
        参数:
            user_id: 用户ID
            required_minutes: 需要的分钟数
        
        返回:
            Dict: 配额检查结果
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        remaining_quota = user.remaining_quota_minutes
        is_sufficient = remaining_quota >= required_minutes
        shortage = max(0, required_minutes - remaining_quota)
        
        plan_config = self.PRICING_CONFIG["subscription_plans"].get(
            user.subscription_tier
        )
        overage_allowed = plan_config.get("overage_allowed", False) if plan_config else False
        
        return {
            "user_id": str(user_id),
            "subscription_tier": user.subscription_tier.value,
            "remaining_quota": remaining_quota,
            "required_minutes": required_minutes,
            "is_sufficient": is_sufficient,
            "shortage": shortage,
            "overage_allowed": overage_allowed,
            "can_proceed": is_sufficient or overage_allowed,
        }
    
    def estimate_monthly_cost(
        self,
        subscription_tier: SubscriptionTier,
        estimated_usage_minutes: float
    ) -> Dict:
        """预估月度费用
        
        参数:
            subscription_tier: 订阅层级
            estimated_usage_minutes: 预估使用分钟数
        
        返回:
            Dict: 费用预估
        """
        plan_config = self.PRICING_CONFIG["subscription_plans"].get(
            subscription_tier
        )
        if not plan_config:
            raise ValueError(f"无效的订阅层级: {subscription_tier}")
        
        monthly_price = plan_config["monthly_price"]
        monthly_quota = plan_config["monthly_quota"]
        
        if subscription_tier == SubscriptionTier.PAY_PER_USE:
            # 按量付费：全部按使用量计费
            total_cost = estimated_usage_minutes * plan_config["rate"]
            overage_cost = 0.0
        elif estimated_usage_minutes <= monthly_quota:
            # 配额充足
            total_cost = monthly_price
            overage_cost = 0.0
        else:
            # 需要超额付费
            overage_minutes = estimated_usage_minutes - monthly_quota
            overage_rate = plan_config.get(
                "overage_rate",
                self.PRICING_CONFIG["overage_rate"]
            )
            overage_cost = overage_minutes * overage_rate
            total_cost = monthly_price + overage_cost
        
        return {
            "subscription_tier": subscription_tier.value,
            "plan_name": plan_config["name"],
            "monthly_price": monthly_price,
            "monthly_quota": monthly_quota,
            "estimated_usage_minutes": estimated_usage_minutes,
            "overage_minutes": max(0, estimated_usage_minutes - monthly_quota),
            "overage_cost": overage_cost,
            "total_cost": total_cost,
            "currency": "CNY",
        }
    
    def get_pricing_plans(self) -> List[Dict]:
        """获取所有定价计划
        
        返回:
            List[Dict]: 定价计划列表
        """
        plans = []
        for tier, config in self.PRICING_CONFIG["subscription_plans"].items():
            plans.append({
                "tier": tier.value,
                "name": config["name"],
                "monthly_price": config["monthly_price"],
                "monthly_quota": config["monthly_quota"],
                "overage_allowed": config.get("overage_allowed", False),
                "overage_rate": config.get("overage_rate", 0.0),
                "rate": config.get("rate", 0.0),
            })
        return plans
    
    def estimate_export_cost_with_details(
        self,
        user_id: uuid.UUID,
        video_duration_minutes: float
    ) -> Dict:
        """预估导出费用并提供详细信息
        
        在导出前显示预估费用和用户剩余额度，帮助用户做出决策。
        
        参数:
            user_id: 用户ID
            video_duration_minutes: 视频时长（分钟）
        
        返回:
            Dict: 详细的费用预估信息
        
        验证：需求6.5
        """
        # 获取用户信息
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 计算费用
        cost_details = self.calculate_export_cost(user_id, video_duration_minutes)
        
        # 检查配额
        quota_check = self.check_quota_availability(user_id, video_duration_minutes)
        
        # 生成建议消息
        if not quota_check["can_proceed"]:
            recommendation = "配额不足且不允许超额使用。建议升级到专业版或企业版。"
        elif cost_details["needs_payment"]:
            if user.subscription_tier == SubscriptionTier.PAY_PER_USE:
                recommendation = f"按量付费模式，本次导出需支付 ¥{cost_details['total_cost']:.2f}"
            else:
                recommendation = f"配额不足，超额使用需支付 ¥{cost_details['overage_cost']:.2f}"
        else:
            recommendation = f"使用配额 {cost_details['quota_used']:.2f} 分钟，无需额外支付"
        
        return {
            "user_id": str(user_id),
            "subscription_tier": user.subscription_tier.value,
            "subscription_name": self.PRICING_CONFIG["subscription_plans"][user.subscription_tier]["name"],
            "video_duration_minutes": video_duration_minutes,
            "current_quota": user.remaining_quota_minutes,
            "quota_after_export": max(0, user.remaining_quota_minutes - cost_details["quota_used"]),
            "cost_breakdown": {
                "quota_used": cost_details["quota_used"],
                "overage_minutes": cost_details["overage_minutes"],
                "base_cost": cost_details["base_cost"],
                "overage_cost": cost_details["overage_cost"],
                "total_cost": cost_details["total_cost"],
            },
            "needs_payment": cost_details["needs_payment"],
            "can_proceed": quota_check["can_proceed"],
            "recommendation": recommendation,
            "currency": "CNY",
        }
    
    def confirm_export_with_cost(
        self,
        user_id: uuid.UUID,
        video_duration_minutes: float,
        user_confirmed: bool
    ) -> Dict:
        """确认导出并验证费用
        
        在用户确认费用后才开始导出处理。
        
        参数:
            user_id: 用户ID
            video_duration_minutes: 视频时长（分钟）
            user_confirmed: 用户是否确认费用
        
        返回:
            Dict: 确认结果
        
        验证：需求6.7
        """
        # 获取费用预估
        estimate = self.estimate_export_cost_with_details(user_id, video_duration_minutes)
        
        if not user_confirmed:
            return {
                "confirmed": False,
                "can_proceed": False,
                "message": "用户未确认费用，导出已取消",
                "estimate": estimate,
            }
        
        if not estimate["can_proceed"]:
            return {
                "confirmed": True,
                "can_proceed": False,
                "message": "配额不足且不允许超额使用，无法继续导出",
                "estimate": estimate,
            }
        
        # 用户已确认且可以继续
        return {
            "confirmed": True,
            "can_proceed": True,
            "message": "费用已确认，可以开始导出",
            "estimate": estimate,
        }
