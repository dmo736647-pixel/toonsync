"""敏感信息加密服务"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
from typing import Optional

from app.core.config import settings


class EncryptionService:
    """敏感信息加密服务
    
    用于加密存储敏感信息，如支付信息、API密钥等
    
    需求：11.5
    """
    
    def __init__(self):
        # 从配置中获取加密密钥
        # 在生产环境中，应该使用环境变量或密钥管理服务
        self.encryption_key = self._derive_key(settings.SECRET_KEY)
        self.cipher = Fernet(self.encryption_key)
    
    def _derive_key(self, password: str) -> bytes:
        """
        从密码派生加密密钥
        
        参数:
            password: 主密码
        
        返回:
            派生的加密密钥
        """
        # 使用PBKDF2派生密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'short-drama-platform-salt',  # 在生产环境中应使用随机盐
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """
        加密数据
        
        参数:
            data: 要加密的明文数据
        
        返回:
            加密后的数据（Base64编码）
        """
        if not data:
            return ""
        
        encrypted_data = self.cipher.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据
        
        参数:
            encrypted_data: 加密的数据（Base64编码）
        
        返回:
            解密后的明文数据
        """
        if not encrypted_data:
            return ""
        
        decrypted_data = self.cipher.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    def encrypt_payment_info(self, payment_info: dict) -> dict:
        """
        加密支付信息
        
        参数:
            payment_info: 支付信息字典，包含敏感字段
        
        返回:
            加密后的支付信息字典
        """
        encrypted_info = payment_info.copy()
        
        # 加密敏感字段
        sensitive_fields = ['card_number', 'cvv', 'account_number', 'routing_number']
        
        for field in sensitive_fields:
            if field in encrypted_info and encrypted_info[field]:
                encrypted_info[field] = self.encrypt(str(encrypted_info[field]))
        
        return encrypted_info
    
    def decrypt_payment_info(self, encrypted_info: dict) -> dict:
        """
        解密支付信息
        
        参数:
            encrypted_info: 加密的支付信息字典
        
        返回:
            解密后的支付信息字典
        """
        decrypted_info = encrypted_info.copy()
        
        # 解密敏感字段
        sensitive_fields = ['card_number', 'cvv', 'account_number', 'routing_number']
        
        for field in sensitive_fields:
            if field in decrypted_info and decrypted_info[field]:
                decrypted_info[field] = self.decrypt(decrypted_info[field])
        
        return decrypted_info
    
    def mask_sensitive_data(self, data: str, visible_chars: int = 4) -> str:
        """
        遮蔽敏感数据（用于显示）
        
        参数:
            data: 敏感数据
            visible_chars: 可见字符数
        
        返回:
            遮蔽后的数据（例如：**** **** **** 1234）
        """
        if not data or len(data) <= visible_chars:
            return data
        
        masked_part = '*' * (len(data) - visible_chars)
        visible_part = data[-visible_chars:]
        
        return masked_part + visible_part


# 全局加密服务实例
encryption_service = EncryptionService()


def get_encryption_service() -> EncryptionService:
    """获取加密服务的依赖注入函数"""
    return encryption_service
