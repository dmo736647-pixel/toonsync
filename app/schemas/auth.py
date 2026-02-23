"""认证相关的Pydantic模式"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

from app.models.user import SubscriptionTier


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50)


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用户响应"""
    id: uuid.UUID
    email: str
    subscription_tier: SubscriptionTier
    remaining_quota_minutes: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """用户登录响应"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
