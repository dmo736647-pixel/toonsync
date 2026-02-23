"""额度管理和使用统计服务"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from app.models.user import User, SubscriptionTier


class UsageRecord:
    """使用记录（简化版，实际应该是数据库模型）"""
    def __init__(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        action_type: str,
        duration_minutes: float,
        cost: float,
        created_at: datetime
    ):
        self.id = id
        self.user_id = user_id
        self.action_type = action_type
        self.duration_minutes = duration_minutes
        self.cost = cost
        self.created_at = created_at


class UsageService:
    """额度管理和使用统计服务类"""
    
    # 按量付费价格（¥/分钟）
    PAY_PER_USE_PRICE = 10.0
    
    def __init__(self, db: Session):
        self.db = db
        # 注意：在实际实现中，应该创建UsageRecord数据库模型
        # 这里为了简化，使用内存存储
        self._usage_records = []
    
    def deduct_quota(
        self,
        user_id: uuid.UUID,
        duration_minutes: float,
        action_type: str = "video_export"
    ) -> tuple[User, float]:
        """
        扣减用户额度
        
        参数:
            user_id: 用户ID
            duration_minutes: 使用时长（分钟）
            action_type: 操作类型
        
        返回:
            tuple[User, float]: 更新后的用户对象和扣减的费用
        
        异常:
            ValueError: 用户不存在或额度不足
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 检查额度是否足够
        if user.remaining_quota_minutes < duration_minutes:
            # 如果是按量付费，可以超额使用
            if user.subscription_tier == SubscriptionTier.PAY_PER_USE:
                cost = duration_minutes * self.PAY_PER_USE_PRICE
            else:
                raise ValueError(
                    f"额度不足。需要{duration_minutes}分钟，剩余{user.remaining_quota_minutes}分钟"
                )
        else:
            cost = 0.0
        
        # 扣减额度
        user.remaining_quota_minutes -= duration_minutes
        if user.remaining_quota_minutes < 0:
            user.remaining_quota_minutes = 0
        
        # 记录使用
        self._record_usage(user_id, action_type, duration_minutes, cost)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user, cost
    
    def restore_quota(
        self,
        user_id: uuid.UUID,
        duration_minutes: float
    ) -> User:
        """
        恢复用户额度（例如取消操作时）
        
        参数:
            user_id: 用户ID
            duration_minutes: 恢复时长（分钟）
        
        返回:
            User: 更新后的用户对象
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        user.remaining_quota_minutes += duration_minutes
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def _record_usage(
        self,
        user_id: uuid.UUID,
        action_type: str,
        duration_minutes: float,
        cost: float
    ):
        """
        记录使用情况
        
        参数:
            user_id: 用户ID
            action_type: 操作类型
            duration_minutes: 使用时长
            cost: 费用
        """
        record = UsageRecord(
            id=uuid.uuid4(),
            user_id=user_id,
            action_type=action_type,
            duration_minutes=duration_minutes,
            cost=cost,
            created_at=datetime.utcnow()
        )
        self._usage_records.append(record)
    
    def get_usage_statistics(
        self,
        user_id: uuid.UUID,
        days: int = 30
    ) -> dict:
        """
        获取用户使用统计
        
        参数:
            user_id: 用户ID
            days: 统计天数
        
        返回:
            dict: 使用统计信息
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 计算时间范围
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 过滤用户的使用记录
        user_records = [
            r for r in self._usage_records
            if r.user_id == user_id and r.created_at >= start_date
        ]
        
        # 计算统计数据
        total_duration = sum(r.duration_minutes for r in user_records)
        total_cost = sum(r.cost for r in user_records)
        record_count = len(user_records)
        
        # 按操作类型分组
        by_action_type = {}
        for record in user_records:
            if record.action_type not in by_action_type:
                by_action_type[record.action_type] = {
                    "count": 0,
                    "duration_minutes": 0.0,
                    "cost": 0.0
                }
            by_action_type[record.action_type]["count"] += 1
            by_action_type[record.action_type]["duration_minutes"] += record.duration_minutes
            by_action_type[record.action_type]["cost"] += record.cost
        
        return {
            "user_id": str(user_id),
            "subscription_tier": user.subscription_tier.value,
            "remaining_quota_minutes": user.remaining_quota_minutes,
            "period_days": days,
            "total_usage_minutes": total_duration,
            "total_cost": total_cost,
            "usage_count": record_count,
            "by_action_type": by_action_type,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat()
        }
    
    def get_usage_history(
        self,
        user_id: uuid.UUID,
        limit: int = 50
    ) -> List[dict]:
        """
        获取用户使用历史
        
        参数:
            user_id: 用户ID
            limit: 返回记录数量限制
        
        返回:
            List[dict]: 使用记录列表
        """
        # 过滤用户的使用记录
        user_records = [
            r for r in self._usage_records
            if r.user_id == user_id
        ]
        
        # 按时间倒序排序
        user_records.sort(key=lambda r: r.created_at, reverse=True)
        
        # 限制数量
        user_records = user_records[:limit]
        
        # 转换为字典
        return [
            {
                "id": str(r.id),
                "action_type": r.action_type,
                "duration_minutes": r.duration_minutes,
                "cost": r.cost,
                "created_at": r.created_at.isoformat()
            }
            for r in user_records
        ]
    
    def calculate_export_cost(
        self,
        user_id: uuid.UUID,
        video_duration_minutes: float
    ) -> dict:
        """
        计算导出费用
        
        参数:
            user_id: 用户ID
            video_duration_minutes: 视频时长（分钟）
        
        返回:
            dict: 费用信息
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        remaining_quota = user.remaining_quota_minutes
        
        # 计算费用
        if remaining_quota >= video_duration_minutes:
            # 额度充足，无需付费
            cost = 0.0
            needs_payment = False
            quota_after = remaining_quota - video_duration_minutes
        else:
            # 额度不足
            if user.subscription_tier == SubscriptionTier.PAY_PER_USE:
                # 按量付费，计算超额费用
                cost = video_duration_minutes * self.PAY_PER_USE_PRICE
                needs_payment = True
                quota_after = 0.0
            else:
                # 订阅制用户，需要升级或购买额度
                shortage = video_duration_minutes - remaining_quota
                cost = shortage * self.PAY_PER_USE_PRICE
                needs_payment = True
                quota_after = 0.0
        
        return {
            "user_id": str(user_id),
            "subscription_tier": user.subscription_tier.value,
            "video_duration_minutes": video_duration_minutes,
            "remaining_quota_minutes": remaining_quota,
            "quota_after_export": quota_after,
            "cost": cost,
            "needs_payment": needs_payment,
            "message": self._get_cost_message(
                user.subscription_tier,
                remaining_quota,
                video_duration_minutes,
                cost,
                needs_payment
            )
        }
    
    def _get_cost_message(
        self,
        tier: SubscriptionTier,
        remaining_quota: float,
        duration: float,
        cost: float,
        needs_payment: bool
    ) -> str:
        """生成费用提示消息"""
        if not needs_payment:
            return f"使用额度：{duration}分钟，剩余额度：{remaining_quota - duration}分钟"
        else:
            if tier == SubscriptionTier.PAY_PER_USE:
                return f"按量付费：{duration}分钟 × ¥{self.PAY_PER_USE_PRICE}/分钟 = ¥{cost}"
            else:
                shortage = duration - remaining_quota
                return f"额度不足{shortage}分钟，需支付：¥{cost}。建议升级订阅计划。"
