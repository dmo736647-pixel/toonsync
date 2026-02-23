"""订阅相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.user import SubscriptionTier


class SubscriptionPlanInfo(BaseModel):
    """订阅计划信息"""
    name: str
    quota_minutes: float
    price: Optional[float] = None
    price_per_minute: Optional[float] = None
    duration_days: int


class SubscriptionPlansResponse(BaseModel):
    """订阅计划列表响应"""
    plans: dict[SubscriptionTier, SubscriptionPlanInfo]


class CreateSubscriptionRequest(BaseModel):
    """创建订阅请求"""
    plan: SubscriptionTier
    auto_renew: bool = True


class SubscriptionResponse(BaseModel):
    """订阅响应"""
    id: uuid.UUID
    user_id: uuid.UUID
    plan: SubscriptionTier
    quota_minutes: float
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SwitchPlanRequest(BaseModel):
    """切换订阅计划请求"""
    new_plan: SubscriptionTier


class SubscriptionStatusResponse(BaseModel):
    """订阅状态响应"""
    is_active: bool
    is_expired: bool
    current_plan: SubscriptionTier
    remaining_quota_minutes: float
    active_subscription: Optional[SubscriptionResponse] = None
