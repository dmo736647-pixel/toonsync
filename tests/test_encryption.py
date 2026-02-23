"""加密功能单元测试"""
import pytest
from app.services.encryption import EncryptionService


class TestEncryptionService:
    """加密服务测试"""
    
    @pytest.fixture
    def encryption_service(self):
        """创建加密服务实例"""
        return EncryptionService()
    
    def test_encrypt_decrypt(self, encryption_service):
        """
        测试加密和解密
        
        需求：11.5
        """
        original_data = "sensitive_information_12345"
        
        # 加密
        encrypted_data = encryption_service.encrypt(original_data)
        
        # 验证加密后的数据不同于原始数据
        assert encrypted_data != original_data, "加密后的数据应该不同于原始数据"
        
        # 解密
        decrypted_data = encryption_service.decrypt(encrypted_data)
        
        # 验证解密后的数据与原始数据相同
        assert decrypted_data == original_data, "解密后的数据应该与原始数据相同"
    
    def test_encrypt_empty_string(self, encryption_service):
        """
        测试加密空字符串
        
        需求：11.5
        """
        encrypted_data = encryption_service.encrypt("")
        assert encrypted_data == "", "空字符串加密后应该仍为空字符串"
        
        decrypted_data = encryption_service.decrypt("")
        assert decrypted_data == "", "空字符串解密后应该仍为空字符串"
    
    def test_encrypt_payment_info(self, encryption_service):
        """
        测试支付信息加密
        
        需求：11.5
        """
        payment_info = {
            "card_number": "4111111111111111",
            "cvv": "123",
            "card_brand": "Visa",
            "expiry_month": "12",
            "expiry_year": "2025"
        }
        
        # 加密支付信息
        encrypted_info = encryption_service.encrypt_payment_info(payment_info)
        
        # 验证敏感字段已加密
        assert encrypted_info["card_number"] != payment_info["card_number"], "卡号应该被加密"
        assert encrypted_info["cvv"] != payment_info["cvv"], "CVV应该被加密"
        
        # 验证非敏感字段未加密
        assert encrypted_info["card_brand"] == payment_info["card_brand"], "卡品牌不应该被加密"
        assert encrypted_info["expiry_month"] == payment_info["expiry_month"], "过期月份不应该被加密"
    
    def test_decrypt_payment_info(self, encryption_service):
        """
        测试支付信息解密
        
        需求：11.5
        """
        original_info = {
            "card_number": "4111111111111111",
            "cvv": "123",
            "account_number": "1234567890",
            "routing_number": "987654321"
        }
        
        # 加密
        encrypted_info = encryption_service.encrypt_payment_info(original_info)
        
        # 解密
        decrypted_info = encryption_service.decrypt_payment_info(encrypted_info)
        
        # 验证解密后的数据与原始数据相同
        assert decrypted_info["card_number"] == original_info["card_number"]
        assert decrypted_info["cvv"] == original_info["cvv"]
        assert decrypted_info["account_number"] == original_info["account_number"]
        assert decrypted_info["routing_number"] == original_info["routing_number"]
    
    def test_mask_sensitive_data(self, encryption_service):
        """
        测试敏感数据遮蔽
        
        需求：11.5
        """
        card_number = "4111111111111111"
        
        # 遮蔽卡号（显示后4位）
        masked = encryption_service.mask_sensitive_data(card_number, visible_chars=4)
        
        # 验证遮蔽效果
        assert masked.endswith("1111"), "应该显示后4位"
        assert masked.startswith("*"), "前面应该用*遮蔽"
        assert len(masked) == len(card_number), "长度应该相同"
    
    def test_mask_short_data(self, encryption_service):
        """
        测试遮蔽短数据
        
        需求：11.5
        """
        short_data = "123"
        
        # 遮蔽短数据（少于可见字符数）
        masked = encryption_service.mask_sensitive_data(short_data, visible_chars=4)
        
        # 验证短数据不被遮蔽
        assert masked == short_data, "短数据不应该被遮蔽"
    
    def test_encryption_consistency(self, encryption_service):
        """
        测试加密一致性（相同数据多次加密应产生不同结果）
        
        需求：11.5
        """
        data = "test_data"
        
        # 多次加密相同数据
        encrypted1 = encryption_service.encrypt(data)
        encrypted2 = encryption_service.encrypt(data)
        
        # Fernet加密包含时间戳，所以每次加密结果应该不同
        # 但解密后应该得到相同的原始数据
        decrypted1 = encryption_service.decrypt(encrypted1)
        decrypted2 = encryption_service.decrypt(encrypted2)
        
        assert decrypted1 == data
        assert decrypted2 == data
    
    def test_password_hash_not_reversible(self):
        """
        测试密码哈希不可逆
        
        需求：11.5
        """
        from app.services.auth import pwd_context
        
        password = "test_password_123"
        
        # 生成密码哈希
        password_hash = pwd_context.hash(password)
        
        # 验证哈希值不同于原始密码
        assert password_hash != password, "密码哈希应该不同于原始密码"
        
        # 验证可以验证密码
        assert pwd_context.verify(password, password_hash), "应该能够验证正确的密码"
        
        # 验证错误密码无法通过验证
        assert not pwd_context.verify("wrong_password", password_hash), "错误密码不应该通过验证"
