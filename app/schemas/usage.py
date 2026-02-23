"""额度和使用统计相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Dict, List
from datetime import datetime


class DeductQuotaRequest(BaseModel):
    """扣减额度请求"""
    duration_minutes: float = Field(..., gt=0, description="使用时长（分钟）")
    action_type: str = Field(default="video_export", description="操作类型")


class DeductQuotaResponse(BaseModel):
    """扣减额度响应"""
    remaining_quota_minutes: float
    cost: float
    message: str


class RestoreQuotaRequest(BaseModel):
    """恢复额度请求"""
    duration_minutes: float = Field(..., gt=0, description="恢复时长（分钟）")


class UsageStatisticsResponse(BaseModel):
    """使用统计响应"""
    user_id: str
    subscription_tier: str
    remaining_quota_minutes: float
    period_days: int
    total_usage_minutes: float
    total_cost: float
    usage_count: int
    by_action_type: Dict[str, dict]
    start_date: str
    end_date: str


class UsageRecordResponse(BaseModel):
    """使用记录响应"""
    id: str
    action_type: str
    duration_minutes: float
    cost: float
    created_at: str


class CalculateExportCostRequest(BaseModel):
    """计算导出费用请求"""
    video_duration_minutes: float = Field(..., gt=0, description="视频时长（分钟）")


class CalculateExportCostResponse(BaseModel):
    """计算导出费用响应"""
    user_id: str
    subscription_tier: str
    video_duration_minutes: float
    remaining_quota_minutes: float
    quota_after_export: float
    cost: float
    needs_payment: bool
    message: str
