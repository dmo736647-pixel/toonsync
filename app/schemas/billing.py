"""计费管理相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional, List


class CalculateExportCostRequest(BaseModel):
    """计算导出费用请求"""
    video_duration_minutes: float = Field(
        ...,
        gt=0,
        description="视频时长（分钟）"
    )


class CalculateExportCostResponse(BaseModel):
    """计算导出费用响应"""
    user_id: str
    subscription_tier: str
    video_duration_minutes: float
    remaining_quota: float
    quota_used: float
    overage_minutes: float
    base_cost: float
    overage_cost: float
    total_cost: float
    needs_payment: bool
    currency: str


class CheckQuotaRequest(BaseModel):
    """检查配额请求"""
    required_minutes: float = Field(
        ...,
        gt=0,
        description="需要的分钟数"
    )


class CheckQuotaResponse(BaseModel):
    """检查配额响应"""
    user_id: str
    subscription_tier: str
    remaining_quota: float
    required_minutes: float
    is_sufficient: bool
    shortage: float
    overage_allowed: bool
    can_proceed: bool


class EstimateMonthlyCostRequest(BaseModel):
    """预估月度费用请求"""
    subscription_tier: str = Field(..., description="订阅层级")
    estimated_usage_minutes: float = Field(
        ...,
        gt=0,
        description="预估使用分钟数"
    )


class EstimateMonthlyCostResponse(BaseModel):
    """预估月度费用响应"""
    subscription_tier: str
    plan_name: str
    monthly_price: float
    monthly_quota: float
    estimated_usage_minutes: float
    overage_minutes: float
    overage_cost: float
    total_cost: float
    currency: str


class PricingPlanResponse(BaseModel):
    """定价计划响应"""
    tier: str
    name: str
    monthly_price: float
    monthly_quota: float
    overage_allowed: bool
    overage_rate: float
    rate: float


class ExportConfirmationRequest(BaseModel):
    """导出确认请求"""
    video_duration_minutes: float = Field(
        ...,
        gt=0,
        description="视频时长（分钟）"
    )
    confirmed: bool = Field(..., description="用户是否确认费用")


class ExportConfirmationResponse(BaseModel):
    """导出确认响应"""
    confirmed: bool
    cost_details: CalculateExportCostResponse
    message: str
    can_proceed: bool


class EstimateExportCostRequest(BaseModel):
    """预估导出费用请求"""
    video_duration_minutes: float = Field(
        ...,
        gt=0,
        description="视频时长（分钟）"
    )


class CostBreakdown(BaseModel):
    """费用明细"""
    quota_used: float
    overage_minutes: float
    base_cost: float
    overage_cost: float
    total_cost: float


class EstimateExportCostResponse(BaseModel):
    """预估导出费用响应"""
    user_id: str
    subscription_tier: str
    subscription_name: str
    video_duration_minutes: float
    current_quota: float
    quota_after_export: float
    cost_breakdown: CostBreakdown
    needs_payment: bool
    can_proceed: bool
    recommendation: str
    currency: str


class ConfirmExportRequest(BaseModel):
    """确认导出请求"""
    video_duration_minutes: float = Field(
        ...,
        gt=0,
        description="视频时长（分钟）"
    )
    user_confirmed: bool = Field(..., description="用户是否确认费用")


class ConfirmExportResponse(BaseModel):
    """确认导出响应"""
    confirmed: bool
    can_proceed: bool
    message: str
    estimate: EstimateExportCostResponse
