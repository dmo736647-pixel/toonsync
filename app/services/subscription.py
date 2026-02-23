"""订阅管理服务"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid

from app.models.user import User, SubscriptionTier
from app.models.subscription import Subscription


class SubscriptionService:
    """订阅管理服务类"""
    
    # 订阅计划配置
    SUBSCRIPTION_PLANS = {
        SubscriptionTier.FREE: {
            "name": "基础版（免费）",
            "quota_minutes": 5.0,
            "price": 0.0,
            "duration_days": 30,
        },
        SubscriptionTier.PAY_PER_USE: {
            "name": "按量付费",
            "quota_minutes": 0.0,  # 按需购买
            "price_per_minute": 10.0,  # ¥10/分钟
            "duration_days": 0,  # 不限期
        },
        SubscriptionTier.PROFESSIONAL: {
            "name": "专业版",
            "quota_minutes": 50.0,
            "price": 299.0,  # ¥299/月
            "duration_days": 30,
        },
        SubscriptionTier.ENTERPRISE: {
            "name": "企业版",
            "quota_minutes": 200.0,
            "price": 999.0,  # ¥999/月
            "duration_days": 30,
        },
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_subscription_plans(self) -> dict:
        """
        获取所有订阅计划
        
        返回:
            dict: 订阅计划配置
        """
        return self.SUBSCRIPTION_PLANS
    
    def create_subscription(
        self,
        user_id: uuid.UUID,
        plan: SubscriptionTier,
        auto_renew: bool = True
    ) -> Subscription:
        """
        创建订阅
        
        参数:
            user_id: 用户ID
            plan: 订阅计划
            auto_renew: 是否自动续费
        
        返回:
            Subscription: 创建的订阅对象
        
        异常:
            ValueError: 用户不存在或计划无效
        """
        # 验证用户存在
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 验证计划有效
        if plan not in self.SUBSCRIPTION_PLANS:
            raise ValueError("无效的订阅计划")
        
        plan_config = self.SUBSCRIPTION_PLANS[plan]
        
        # 计算订阅时间
        start_date = datetime.utcnow()
        if plan_config["duration_days"] > 0:
            end_date = start_date + timedelta(days=plan_config["duration_days"])
        else:
            # 按量付费不限期
            end_date = start_date + timedelta(days=365 * 10)  # 10年后
        
        # 创建订阅
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            quota_minutes=plan_config["quota_minutes"],
            start_date=start_date,
            end_date=end_date,
            auto_renew=auto_renew
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def activate_subscription(
        self,
        user_id: uuid.UUID,
        plan: SubscriptionTier
    ) -> tuple[User, Subscription]:
        """
        激活订阅并更新用户权限
        
        参数:
            user_id: 用户ID
            plan: 订阅计划
        
        返回:
            tuple[User, Subscription]: 更新后的用户和订阅对象
        
        异常:
            ValueError: 用户不存在或计划无效
        """
        # 获取用户
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 创建订阅
        subscription = self.create_subscription(user_id, plan)
        
        # 更新用户订阅层级和额度
        user.subscription_tier = plan
        plan_config = self.SUBSCRIPTION_PLANS[plan]
        
        # 如果是订阅制，增加额度；如果是按量付费，保持当前额度
        if plan in [SubscriptionTier.FREE, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            user.remaining_quota_minutes += plan_config["quota_minutes"]
        
        self.db.commit()
        self.db.refresh(user)
        
        return user, subscription
    
    def check_subscription_expiry(self, user_id: uuid.UUID) -> bool:
        """
        检查订阅是否过期
        
        参数:
            user_id: 用户ID
        
        返回:
            bool: True表示已过期，False表示未过期
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 获取用户的活跃订阅
        active_subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.end_date.desc()).first()
        
        return active_subscription is None
    
    def handle_subscription_expiry(self, user_id: uuid.UUID) -> User:
        """
        处理订阅到期
        
        参数:
            user_id: 用户ID
        
        返回:
            User: 更新后的用户对象
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 检查是否有过期的订阅
        expired_subscriptions = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.end_date <= datetime.utcnow()
        ).all()
        
        if expired_subscriptions:
            # 降级到免费版
            user.subscription_tier = SubscriptionTier.FREE
            user.remaining_quota_minutes = 5.0  # 重置为免费额度
            
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    def switch_subscription_plan(
        self,
        user_id: uuid.UUID,
        new_plan: SubscriptionTier
    ) -> tuple[User, Subscription]:
        """
        切换订阅计划
        
        参数:
            user_id: 用户ID
            new_plan: 新的订阅计划
        
        返回:
            tuple[User, Subscription]: 更新后的用户和新订阅对象
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 结束当前活跃订阅
        active_subscriptions = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.end_date > datetime.utcnow()
        ).all()
        
        for sub in active_subscriptions:
            sub.end_date = datetime.utcnow()
        
        # 激活新订阅
        user, new_subscription = self.activate_subscription(user_id, new_plan)
        
        return user, new_subscription
    
    def get_user_subscriptions(
        self,
        user_id: uuid.UUID,
        active_only: bool = False
    ) -> List[Subscription]:
        """
        获取用户的订阅列表
        
        参数:
            user_id: 用户ID
            active_only: 是否只返回活跃订阅
        
        返回:
            List[Subscription]: 订阅列表
        """
        query = self.db.query(Subscription).filter(Subscription.user_id == user_id)
        
        if active_only:
            query = query.filter(Subscription.end_date > datetime.utcnow())
        
        return query.order_by(Subscription.created_at.desc()).all()
    
    def get_active_subscription(self, user_id: uuid.UUID) -> Optional[Subscription]:
        """
        获取用户的活跃订阅
        
        参数:
            user_id: 用户ID
        
        返回:
            Optional[Subscription]: 活跃订阅，如果没有则返回None
        """
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.end_date.desc()).first()
