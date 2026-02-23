"""订阅管理API端点"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.subscription import SubscriptionService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionPlansResponse,
    SubscriptionPlanInfo,
    CreateSubscriptionRequest,
    SubscriptionResponse,
    SwitchPlanRequest,
    SubscriptionStatusResponse,
)


router = APIRouter(prefix="/subscriptions", tags=["订阅管理"])


@router.get("/plans", response_model=dict)
async def get_subscription_plans(
    db: Session = Depends(get_db)
):
    """
    获取所有订阅计划
    
    返回所有可用的订阅计划及其详细信息
    """
    subscription_service = SubscriptionService(db)
    plans = subscription_service.get_subscription_plans()
    
    # 转换为响应格式
    response = {}
    for tier, config in plans.items():
        response[tier.value] = config
    
    return response


@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建订阅
    
    为当前用户创建新的订阅
    """
    subscription_service = SubscriptionService(db)
    
    try:
        subscription = subscription_service.create_subscription(
            user_id=current_user.id,
            plan=request.plan,
            auto_renew=request.auto_renew
        )
        return SubscriptionResponse.model_validate(subscription)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/activate", response_model=SubscriptionResponse)
async def activate_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    激活订阅
    
    激活订阅并更新用户权限和额度
    """
    subscription_service = SubscriptionService(db)
    
    try:
        user, subscription = subscription_service.activate_subscription(
            user_id=current_user.id,
            plan=request.plan
        )
        return SubscriptionResponse.model_validate(subscription)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取订阅状态
    
    返回当前用户的订阅状态和额度信息
    """
    subscription_service = SubscriptionService(db)
    
    is_expired = subscription_service.check_subscription_expiry(current_user.id)
    active_subscription = subscription_service.get_active_subscription(current_user.id)
    
    return SubscriptionStatusResponse(
        is_active=not is_expired,
        is_expired=is_expired,
        current_plan=current_user.subscription_tier,
        remaining_quota_minutes=current_user.remaining_quota_minutes,
        active_subscription=SubscriptionResponse.model_validate(active_subscription) if active_subscription else None
    )


@router.post("/switch", response_model=SubscriptionResponse)
async def switch_subscription_plan(
    request: SwitchPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    切换订阅计划
    
    切换到新的订阅计划
    """
    subscription_service = SubscriptionService(db)
    
    try:
        user, subscription = subscription_service.switch_subscription_plan(
            user_id=current_user.id,
            new_plan=request.new_plan
        )
        return SubscriptionResponse.model_validate(subscription)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/history", response_model=List[SubscriptionResponse])
async def get_subscription_history(
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取订阅历史
    
    返回用户的所有订阅记录
    """
    subscription_service = SubscriptionService(db)
    
    subscriptions = subscription_service.get_user_subscriptions(
        user_id=current_user.id,
        active_only=active_only
    )
    
    return [SubscriptionResponse.model_validate(sub) for sub in subscriptions]


@router.post("/handle-expiry", response_model=dict)
async def handle_subscription_expiry(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    处理订阅到期
    
    检查并处理过期的订阅，降级到免费版
    """
    subscription_service = SubscriptionService(db)
    
    try:
        user = subscription_service.handle_subscription_expiry(current_user.id)
        return {
            "message": "订阅到期处理完成",
            "current_plan": user.subscription_tier.value,
            "remaining_quota_minutes": user.remaining_quota_minutes
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
