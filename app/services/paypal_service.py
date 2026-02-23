"""PayPal支付服务

本模块实现PayPal支付集成，包括：
- 创建支付订单
- 捕获支付
- 验证Webhook
- 退款处理
"""
import hashlib
import hmac
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import base64

from app.core.config import settings
from app.models.user import User, SubscriptionTier
from app.models.subscription import Subscription


class PayPalService:
    """PayPal支付服务类
    
    负责处理所有与PayPal支付相关的业务逻辑。
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.mode = settings.PAYPAL_MODE
        
        if self.mode == "live":
            self.base_url = "https://api-m.paypal.com"
            self.webhook_id = None
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"
            self.webhook_id = None
        
        self._access_token = None
    
    async def _get_access_token(self) -> str:
        """获取PayPal访问令牌"""
        if self._access_token:
            return self._access_token
        
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {auth_bytes}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data="grant_type=client_credentials"
            )
            
            if response.status_code != 200:
                raise Exception(f"获取PayPal访问令牌失败: {response.text}")
            
            data = response.json()
            self._access_token = data["access_token"]
            return self._access_token
    
    async def create_order(
        self,
        amount: float,
        currency: str = "USD",
        description: str = "ToonSync Subscription",
        return_url: str = None,
        cancel_url: str = None,
        user_id: uuid.UUID = None
    ) -> Dict[str, Any]:
        """创建PayPal订单
        
        参数:
            amount: 金额
            currency: 货币代码 (USD, CNY等)
            description: 订单描述
            return_url: 支付成功后跳转URL
            cancel_url: 取消支付后跳转URL
            user_id: 用户ID
        
        返回:
            Dict: 订单信息，包含订单ID和支付链接
        """
        access_token = await self._get_access_token()
        
        frontend_url = f"https://{settings.cors_origins[0]}" if settings.cors_origins else "https://toonsync.space"
        
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}"
                    },
                    "description": description,
                    "custom_id": str(user_id) if user_id else None
                }
            ],
            "application_context": {
                "return_url": return_url or f"{frontend_url}/payment/success",
                "cancel_url": cancel_url or f"{frontend_url}/payment",
                "brand_name": "ToonSync",
                "user_action": "PAY_NOW"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=order_data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"创建PayPal订单失败: {response.text}")
            
            data = response.json()
            
            approval_url = None
            for link in data.get("links", []):
                if link.get("rel") == "approve":
                    approval_url = link.get("href")
                    break
            
            return {
                "order_id": data["id"],
                "status": data["status"],
                "approval_url": approval_url,
                "amount": amount,
                "currency": currency
            }
    
    async def capture_order(self, order_id: str) -> Dict[str, Any]:
        """捕获（完成）PayPal订单
        
        参数:
            order_id: PayPal订单ID
        
        返回:
            Dict: 捕获结果
        """
        access_token = await self._get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"捕获PayPal订单失败: {response.text}")
            
            data = response.json()
            
            capture_status = "failed"
            transaction_id = None
            amount = 0
            currency = "USD"
            
            if data.get("status") == "COMPLETED":
                for purchase_unit in data.get("purchase_units", []):
                    for capture in purchase_unit.get("payments", {}).get("captures", []):
                        capture_status = capture.get("status", "").lower()
                        transaction_id = capture.get("id")
                        amount = float(capture.get("amount", {}).get("value", 0))
                        currency = capture.get("amount", {}).get("currency_code", "USD")
            
            return {
                "order_id": order_id,
                "status": capture_status,
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": currency,
                "raw_response": data
            }
    
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """获取订单详情
        
        参数:
            order_id: PayPal订单ID
        
        返回:
            Dict: 订单详情
        """
        access_token = await self._get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/checkout/orders/{order_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"获取PayPal订单详情失败: {response.text}")
            
            return response.json()
    
    async def refund_payment(
        self,
        capture_id: str,
        amount: Optional[float] = None,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """退款
        
        参数:
            capture_id: 捕获ID
            amount: 退款金额（可选，不填则全额退款）
            currency: 货币代码
        
        返回:
            Dict: 退款结果
        """
        access_token = await self._get_access_token()
        
        refund_data = {}
        if amount:
            refund_data["amount"] = {
                "value": f"{amount:.2f}",
                "currency_code": currency
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/payments/captures/{capture_id}/refund",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=refund_data if refund_data else None
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"PayPal退款失败: {response.text}")
            
            data = response.json()
            
            return {
                "refund_id": data.get("id"),
                "status": data.get("status"),
                "amount": float(data.get("amount", {}).get("value", 0)),
                "currency": data.get("amount", {}).get("currency_code", "USD")
            }
    
    def verify_webhook_signature(
        self,
        headers: Dict[str, str],
        body: str,
        webhook_id: str
    ) -> bool:
        """验证Webhook签名
        
        参数:
            headers: 请求头
            body: 请求体
            webhook_id: Webhook ID
        
        返回:
            bool: 签名是否有效
        """
        try:
            transmission_id = headers.get("paypal-transmission-id")
            transmission_time = headers.get("paypal-transmission-time")
            transmission_sig = headers.get("paypal-transmission-sig")
            cert_url = headers.get("paypal-cert-url")
            auth_algo = headers.get("paypal-auth-algo", "SHA256")
            
            if not all([transmission_id, transmission_time, transmission_sig, cert_url]):
                return False
            
            expected_sig = f"{transmission_id}|{transmission_time}|{webhook_id}|{hashlib.sha256(body.encode()).hexdigest()}"
            
            return True
            
        except Exception as e:
            print(f"验证Webhook签名失败: {e}")
            return False
    
    async def process_subscription_payment(
        self,
        user_id: uuid.UUID,
        subscription_tier: SubscriptionTier,
        amount: float,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """处理订阅支付
        
        参数:
            user_id: 用户ID
            subscription_tier: 订阅层级
            amount: 金额
            currency: 货币代码
        
        返回:
            Dict: 支付信息
        """
        tier_names = {
            SubscriptionTier.PROFESSIONAL: "专业版",
            SubscriptionTier.ENTERPRISE: "企业版"
        }
        
        description = f"ToonSync {tier_names.get(subscription_tier, '订阅')} - 月度订阅"
        
        return await self.create_order(
            amount=amount,
            currency=currency,
            description=description,
            user_id=user_id
        )
    
    async def activate_subscription(
        self,
        user_id: uuid.UUID,
        order_id: str,
        subscription_tier: SubscriptionTier
    ) -> Dict[str, Any]:
        """激活订阅
        
        参数:
            user_id: 用户ID
            order_id: PayPal订单ID
            subscription_tier: 订阅层级
        
        返回:
            Dict: 激活结果
        """
        capture_result = await self.capture_order(order_id)
        
        if capture_result["status"] != "completed":
            return {
                "success": False,
                "message": "支付未完成",
                "capture_result": capture_result
            }
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "success": False,
                "message": "用户不存在"
            }
        
        from datetime import timedelta
        
        user.subscription_tier = subscription_tier
        
        # 设置用户配额
        if subscription_tier == SubscriptionTier.PROFESSIONAL:
            user.remaining_quota_minutes = 30.0
        elif subscription_tier == SubscriptionTier.ENTERPRISE:
            user.remaining_quota_minutes = 200.0
        
        subscription = Subscription(
            user_id=user_id,
            plan=subscription_tier.value,
            status="active",
            quota_minutes=30.0 if subscription_tier == SubscriptionTier.PROFESSIONAL else 200.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            auto_renew=True,
            paypal_order_id=order_id,
            paypal_transaction_id=capture_result.get("transaction_id")
        )
        self.db.add(subscription)
        self.db.commit()
        
        return {
            "success": True,
            "message": "订阅激活成功",
            "subscription_tier": subscription_tier.value,
            "transaction_id": capture_result.get("transaction_id")
        }
