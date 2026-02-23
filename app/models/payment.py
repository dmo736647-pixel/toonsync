"""支付信息模型"""
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, GUID


class PaymentMethod(BaseModel):
    """支付方式模型
    
    存储用户的支付信息（加密）
    
    需求：11.5
    """
    
    __tablename__ = "payment_methods"
    
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_type = Column(String(50), nullable=False)  # credit_card, debit_card, bank_account
    
    # 加密的支付信息
    encrypted_card_number = Column(Text, nullable=True)  # 加密的卡号
    encrypted_cvv = Column(Text, nullable=True)  # 加密的CVV
    encrypted_account_number = Column(Text, nullable=True)  # 加密的账号
    encrypted_routing_number = Column(Text, nullable=True)  # 加密的路由号
    
    # 非敏感信息（可以明文存储）
    card_brand = Column(String(50), nullable=True)  # Visa, MasterCard, etc.
    last_four_digits = Column(String(4), nullable=True)  # 卡号后四位（用于显示）
    expiry_month = Column(String(2), nullable=True)
    expiry_year = Column(String(4), nullable=True)
    billing_name = Column(String(255), nullable=True)
    billing_address = Column(Text, nullable=True)
    
    is_default = Column(String(10), default="false", nullable=False)  # 是否为默认支付方式
    
    # 关系
    user = relationship("User", back_populates="payment_methods")
