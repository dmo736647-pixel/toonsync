"""计费管理API端点"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, SubscriptionTier
from app.services.billing import BillingService
from app.schemas.billing import (
    CalculateExportCostRequest,
    CalculateExportCostResponse,
    CheckQuotaRequest,
    CheckQuotaResponse,
    EstimateMonthlyCostRequest,
    EstimateMonthlyCostResponse,
    PricingPlanResponse,
    ExportConfirmationRequest,
    ExportConfirmationResponse,
    EstimateExportCostRequest,
    EstimateExportCostResponse,
    ConfirmExportRequest,
    ConfirmExportResponse,
)


router = APIRouter(prefix="/billing", tags=["billing"])


@router.post(
    "/calculate-export-cost",
    response_model=CalculateExportCostResponse,
    summary="计算导出费用"
)
def calculate_export_cost(
    request: CalculateExportCostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    计算导出费用
    
    根据用户订阅层级和视频时长计算导出费用，包括超额使用的额外费用。
    
    - **video_duration_minutes**: 视频时长（分钟）
    
    返回费用详情，包括基础费用、超额费用和总费用。
    """
    try:
        billing_service = BillingService(db)
        cost_details = billing_service.calculate_export_cost(
            user_id=current_user.id,
            video_duration_minutes=request.video_duration_minutes
        )
        return CalculateExportCostResponse(**cost_details)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/check-quota",
    response_model=CheckQuotaResponse,
    summary="检查配额可用性"
)
def check_quota(
    request: CheckQuotaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    检查配额可用性
    
    检查用户当前配额是否足够完成指定时长的操作。
    
    - **required_minutes**: 需要的分钟数
    
    返回配额检查结果，包括是否充足、缺口和是否允许超额。
    """
    try:
        billing_service = BillingService(db)
        quota_check = billing_service.check_quota_availability(
            user_id=current_user.id,
            required_minutes=request.required_minutes
        )
        return CheckQuotaResponse(**quota_check)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/estimate-monthly-cost",
    response_model=EstimateMonthlyCostResponse,
    summary="预估月度费用"
)
def estimate_monthly_cost(
    request: EstimateMonthlyCostRequest,
    db: Session = Depends(get_db)
):
    """
    预估月度费用
    
    根据订阅层级和预估使用量计算月度费用。
    
    - **subscription_tier**: 订阅层级（FREE, PAY_PER_USE, PROFESSIONAL, ENTERPRISE）
    - **estimated_usage_minutes**: 预估使用分钟数
    
    返回月度费用预估，包括基础费用和超额费用。
    """
    try:
        # 转换订阅层级
        tier = SubscriptionTier(request.subscription_tier)
        
        billing_service = BillingService(db)
        estimate = billing_service.estimate_monthly_cost(
            subscription_tier=tier,
            estimated_usage_minutes=request.estimated_usage_minutes
        )
        return EstimateMonthlyCostResponse(**estimate)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/pricing-plans",
    response_model=List[PricingPlanResponse],
    summary="获取定价计划"
)
def get_pricing_plans(db: Session = Depends(get_db)):
    """
    获取所有定价计划
    
    返回所有可用的订阅计划及其定价信息。
    """
    billing_service = BillingService(db)
    plans = billing_service.get_pricing_plans()
    return [PricingPlanResponse(**plan) for plan in plans]


@router.post(
    "/confirm-export",
    response_model=ExportConfirmationResponse,
    summary="确认导出并计算费用"
)
def confirm_export(
    request: ExportConfirmationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    确认导出并计算费用
    
    在用户确认费用后，返回详细的费用信息和是否可以继续导出。
    
    - **video_duration_minutes**: 视频时长（分钟）
    - **confirmed**: 用户是否确认费用
    
    返回确认结果和费用详情。
    """
    try:
        billing_service = BillingService(db)
        
        # 计算费用
        cost_details = billing_service.calculate_export_cost(
            user_id=current_user.id,
            video_duration_minutes=request.video_duration_minutes
        )
        
        # 检查配额
        quota_check = billing_service.check_quota_availability(
            user_id=current_user.id,
            required_minutes=request.video_duration_minutes
        )
        
        # 判断是否可以继续
        can_proceed = request.confirmed and quota_check["can_proceed"]
        
        # 生成消息
        if not request.confirmed:
            message = "用户未确认费用，无法继续导出"
        elif not quota_check["can_proceed"]:
            message = f"配额不足且不允许超额使用。请升级订阅计划。"
        elif cost_details["needs_payment"]:
            message = f"需要支付 ¥{cost_details['total_cost']:.2f}，用户已确认"
        else:
            message = f"使用配额 {cost_details['quota_used']:.2f} 分钟，无需支付"
        
        return ExportConfirmationResponse(
            confirmed=request.confirmed,
            cost_details=CalculateExportCostResponse(**cost_details),
            message=message,
            can_proceed=can_proceed
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/estimate-export-cost",
    response_model=EstimateExportCostResponse,
    summary="预估导出费用（详细版）"
)
def estimate_export_cost(
    request: EstimateExportCostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    预估导出费用并提供详细信息
    
    在导出前显示预估费用和用户剩余额度，帮助用户做出决策。
    
    - **video_duration_minutes**: 视频时长（分钟）
    
    返回详细的费用预估，包括当前配额、导出后配额、费用明细和建议。
    
    验证：需求6.5
    """
    try:
        billing_service = BillingService(db)
        
        estimate = billing_service.estimate_export_cost_with_details(
            user_id=current_user.id,
            video_duration_minutes=request.video_duration_minutes
        )
        
        return EstimateExportCostResponse(**estimate)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/confirm-export-with-cost",
    response_model=ConfirmExportResponse,
    summary="确认导出并验证费用"
)
def confirm_export_with_cost(
    request: ConfirmExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    确认导出并验证费用
    
    在用户确认费用后才开始导出处理。
    
    - **video_duration_minutes**: 视频时长（分钟）
    - **user_confirmed**: 用户是否确认费用
    
    返回确认结果和详细的费用预估。
    
    验证：需求6.7
    """
    try:
        billing_service = BillingService(db)
        
        result = billing_service.confirm_export_with_cost(
            user_id=current_user.id,
            video_duration_minutes=request.video_duration_minutes,
            user_confirmed=request.user_confirmed
        )
        
        return ConfirmExportResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
