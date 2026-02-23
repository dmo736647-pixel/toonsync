"""用户模型"""
from sqlalchemy import Column, String, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class SubscriptionTier(str, enum.Enum):
    """订阅层级"""
    FREE = "free"
    PAY_PER_USE = "pay_per_use"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class User(BaseModel):
    """用户模型"""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    remaining_quota_minutes = Column(Float, default=5.0, nullable=False)
    
    # 关系
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payment_methods = relationship("PaymentMethod", back_populates="user", cascade="all, delete-orphan")
