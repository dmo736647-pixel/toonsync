"""订阅模型"""
from sqlalchemy import Column, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, GUID
from app.models.user import SubscriptionTier


class Subscription(BaseModel):
    """订阅模型"""
    
    __tablename__ = "subscriptions"
    
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan = Column(SQLEnum(SubscriptionTier), nullable=False)
    status = Column(String(20), default="active", nullable=False)
    quota_minutes = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=True, nullable=False)
    
    # PayPal 支付信息
    paypal_order_id = Column(String(255), nullable=True)
    paypal_transaction_id = Column(String(255), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="subscriptions")
