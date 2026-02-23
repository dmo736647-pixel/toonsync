"""PayPal支付API端点"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, SubscriptionTier
from app.services.paypal_service import PayPalService


router = APIRouter(prefix="/paypal", tags=["paypal"])


class CreateOrderRequest(BaseModel):
    amount: float
    currency: str = "USD"
    subscription_tier: Optional[str] = None


class CaptureOrderRequest(BaseModel):
    order_id: str
    subscription_tier: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: str
    status: str
    approval_url: Optional[str]
    amount: float
    currency: str


class CaptureResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    subscription_tier: Optional[str] = None


@router.post(
    "/create-order",
    response_model=OrderResponse,
    summary="创建PayPal订单"
)
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建PayPal支付订单
    
    - **amount**: 支付金额
    - **currency**: 货币代码 (USD, CNY等)
    - **subscription_tier**: 订阅层级 (可选)
    """
    try:
        paypal_service = PayPalService(db)
        
        subscription_tier = None
        if request.subscription_tier:
            subscription_tier = SubscriptionTier(request.subscription_tier)
        
        result = await paypal_service.process_subscription_payment(
            user_id=current_user.id,
            subscription_tier=subscription_tier or SubscriptionTier.PROFESSIONAL,
            amount=request.amount,
            currency=request.currency
        )
        
        return OrderResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建订单失败: {str(e)}"
        )


@router.post(
    "/capture-order",
    response_model=CaptureResponse,
    summary="捕获PayPal订单"
)
async def capture_order(
    request: CaptureOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    捕获（完成）PayPal订单
    
    在用户完成PayPal支付后调用此接口确认支付。
    
    - **order_id**: PayPal订单ID
    - **subscription_tier**: 订阅层级 (可选)
    """
    try:
        paypal_service = PayPalService(db)
        
        subscription_tier = SubscriptionTier.PROFESSIONAL
        if request.subscription_tier:
            subscription_tier = SubscriptionTier(request.subscription_tier)
        
        result = await paypal_service.activate_subscription(
            user_id=current_user.id,
            order_id=request.order_id,
            subscription_tier=subscription_tier
        )
        
        return CaptureResponse(
            success=result.get("success", False),
            message=result.get("message", ""),
            order_id=request.order_id,
            transaction_id=result.get("transaction_id"),
            subscription_tier=result.get("subscription_tier")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"捕获订单失败: {str(e)}"
        )


@router.post(
    "/webhook",
    summary="PayPal Webhook回调"
)
async def paypal_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    PayPal Webhook回调端点
    
    用于接收PayPal的支付状态通知。
    """
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        paypal_service = PayPalService(db)
        
        event_data = await request.json()
        event_type = event_data.get("event_type")
        
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            resource = event_data.get("resource", {})
            order_id = resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")
            
        elif event_type == "PAYMENT.CAPTURE.DENIED":
            pass
            
        elif event_type == "PAYMENT.CAPTURE.REFUNDED":
            pass
        
        return {"status": "received"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook处理失败: {str(e)}"
        )


@router.get(
    "/order/{order_id}",
    summary="获取订单详情"
)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取PayPal订单详情
    
    - **order_id**: PayPal订单ID
    """
    try:
        paypal_service = PayPalService(db)
        result = await paypal_service.get_order_details(order_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"获取订单详情失败: {str(e)}"
        )
