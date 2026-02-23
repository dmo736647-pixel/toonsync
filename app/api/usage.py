"""额度管理和使用统计API端点"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.usage import UsageService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.usage import (
    DeductQuotaRequest,
    DeductQuotaResponse,
    RestoreQuotaRequest,
    UsageStatisticsResponse,
    UsageRecordResponse,
    CalculateExportCostRequest,
    CalculateExportCostResponse,
)


router = APIRouter(prefix="/usage", tags=["额度管理"])


@router.post("/deduct", response_model=DeductQuotaResponse)
async def deduct_quota(
    request: DeductQuotaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    扣减用户额度
    
    用于视频导出等操作时扣减用户的使用额度
    """
    usage_service = UsageService(db)
    
    try:
        user, cost = usage_service.deduct_quota(
            user_id=current_user.id,
            duration_minutes=request.duration_minutes,
            action_type=request.action_type
        )
        
        return DeductQuotaResponse(
            remaining_quota_minutes=user.remaining_quota_minutes,
            cost=cost,
            message=f"已扣减{request.duration_minutes}分钟额度，剩余{user.remaining_quota_minutes}分钟"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/restore", response_model=dict)
async def restore_quota(
    request: RestoreQuotaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    恢复用户额度
    
    用于取消操作时恢复已扣减的额度
    """
    usage_service = UsageService(db)
    
    try:
        user = usage_service.restore_quota(
            user_id=current_user.id,
            duration_minutes=request.duration_minutes
        )
        
        return {
            "message": f"已恢复{request.duration_minutes}分钟额度",
            "remaining_quota_minutes": user.remaining_quota_minutes
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/statistics", response_model=UsageStatisticsResponse)
async def get_usage_statistics(
    days: int = Query(default=30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取使用统计
    
    返回用户在指定时间范围内的使用统计信息
    """
    usage_service = UsageService(db)
    
    try:
        statistics = usage_service.get_usage_statistics(
            user_id=current_user.id,
            days=days
        )
        
        return UsageStatisticsResponse(**statistics)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/history", response_model=List[UsageRecordResponse])
async def get_usage_history(
    limit: int = Query(default=50, ge=1, le=100, description="返回记录数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取使用历史
    
    返回用户的使用记录列表
    """
    usage_service = UsageService(db)
    
    history = usage_service.get_usage_history(
        user_id=current_user.id,
        limit=limit
    )
    
    return [UsageRecordResponse(**record) for record in history]


@router.post("/calculate-cost", response_model=CalculateExportCostResponse)
async def calculate_export_cost(
    request: CalculateExportCostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    计算导出费用
    
    在导出前预估费用和剩余额度
    """
    usage_service = UsageService(db)
    
    try:
        cost_info = usage_service.calculate_export_cost(
            user_id=current_user.id,
            video_duration_minutes=request.video_duration_minutes
        )
        
        return CalculateExportCostResponse(**cost_info)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/quota", response_model=dict)
async def get_current_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前额度
    
    返回用户的剩余额度信息
    """
    return {
        "user_id": str(current_user.id),
        "subscription_tier": current_user.subscription_tier.value,
        "remaining_quota_minutes": current_user.remaining_quota_minutes
    }
