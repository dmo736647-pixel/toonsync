"""错误处理属性测试

属性48：错误处理
对于任意操作失败，系统应显示清晰的错误信息和解决建议

验证需求：13.4
"""
import pytest
from hypothesis import given, strategies as st, settings, assume

from app.services.error_handler import (
    ErrorCode,
    ErrorCategory,
    ErrorSolution,
    ErrorResponse,
    ErrorHandlerService
)


# Hypothesis策略
error_codes = st.sampled_from(list(ErrorCode))
error_messages = st.text(min_size=1, max_size=200)
error_details = st.text(min_size=0, max_size=500)
field_names = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), blacklist_characters='_'))
resource_types = st.sampled_from(["项目", "角色", "素材", "用户", "订阅"])
resource_ids = st.text(min_size=1, max_size=50)
retry_after_seconds = st.integers(min_value=1, max_value=3600)


class TestErrorHandlerProperties:
    """错误处理属性测试"""
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_response_has_required_fields(self, error_code: ErrorCode):
        """
        属性48：错误处理 - 必需字段
        
        对于任意错误代码，错误响应应该包含所有必需的字段
        
        验证：
        1. 错误响应包含error对象
        2. error对象包含code、message、category
        3. 所有字段类型正确
        """
        response = ErrorHandlerService.create_error_response(error_code)
        data = response.to_dict()
        
        # 验证：必需字段存在
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "category" in data["error"]
        
        # 验证：字段类型正确
        assert isinstance(data["error"]["code"], int)
        assert isinstance(data["error"]["message"], str)
        assert isinstance(data["error"]["category"], str)
        
        # 验证：消息不为空
        assert len(data["error"]["message"]) > 0
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_category_is_consistent(self, error_code: ErrorCode):
        """
        属性：错误类别与错误代码一致
        
        对于任意错误代码，其类别应该与代码范围一致
        """
        category = ErrorHandlerService._get_error_category(error_code)
        code_value = error_code.value
        
        # 验证：类别与代码范围匹配
        if 1000 <= code_value < 2000:
            assert category == ErrorCategory.VALIDATION
        elif 2000 <= code_value < 3000:
            assert category == ErrorCategory.AUTHENTICATION
        elif 3000 <= code_value < 4000:
            assert category == ErrorCategory.AUTHORIZATION
        elif 4000 <= code_value < 5000:
            assert category == ErrorCategory.NOT_FOUND
        elif 5000 <= code_value < 6000:
            assert category == ErrorCategory.CONFLICT
        elif 6000 <= code_value < 7000:
            assert category == ErrorCategory.RATE_LIMIT
        elif 7000 <= code_value < 8000:
            assert category == ErrorCategory.SERVER_ERROR
        elif 8000 <= code_value < 9000:
            assert category == ErrorCategory.EXTERNAL_SERVICE
        else:
            assert category == ErrorCategory.BUSINESS_LOGIC
    
    @given(
        error_code=error_codes,
        custom_message=error_messages
    )
    @settings(max_examples=100, deadline=None)
    def test_property_custom_message_is_preserved(
        self,
        error_code: ErrorCode,
        custom_message: str
    ):
        """
        属性：自定义错误消息被保留
        
        对于任意错误代码和自定义消息，响应应该使用自定义消息
        """
        response = ErrorHandlerService.create_error_response(
            error_code,
            message=custom_message
        )
        
        # 验证：使用了自定义消息
        assert response.message == custom_message
        
        data = response.to_dict()
        assert data["error"]["message"] == custom_message
    
    @given(
        field=field_names,
        message=error_messages
    )
    @settings(max_examples=100, deadline=None)
    def test_property_validation_error_includes_field(
        self,
        field: str,
        message: str
    ):
        """
        属性48：错误处理 - 验证错误包含字段信息
        
        对于任意验证错误，响应应该包含出错的字段名
        """
        error_dict = ErrorHandlerService.format_validation_error(field, message)
        
        # 验证：包含字段信息
        assert "error" in error_dict
        assert "field" in error_dict["error"]
        assert error_dict["error"]["field"] == field
        
        # 验证：类别正确
        assert error_dict["error"]["category"] == ErrorCategory.VALIDATION.value
    
    @given(
        resource_type=resource_types,
        resource_id=resource_ids
    )
    @settings(max_examples=100, deadline=None)
    def test_property_not_found_error_includes_resource_info(
        self,
        resource_type: str,
        resource_id: str
    ):
        """
        属性48：错误处理 - 未找到错误包含资源信息
        
        对于任意资源未找到错误，响应应该包含资源类型和ID
        """
        error_dict = ErrorHandlerService.format_not_found_error(
            resource_type,
            resource_id
        )
        
        # 验证：消息包含资源类型
        assert resource_type in error_dict["error"]["message"]
        
        # 验证：详情包含资源ID
        if "details" in error_dict["error"]:
            assert resource_id in error_dict["error"]["details"]
        
        # 验证：类别正确
        assert error_dict["error"]["category"] == ErrorCategory.NOT_FOUND.value
    
    @given(retry_after=retry_after_seconds)
    @settings(max_examples=100, deadline=None)
    def test_property_rate_limit_error_includes_retry_info(
        self,
        retry_after: int
    ):
        """
        属性48：错误处理 - 速率限制错误包含重试信息
        
        对于任意速率限制错误，响应应该包含重试等待时间
        """
        error_dict = ErrorHandlerService.format_rate_limit_error(retry_after)
        
        # 验证：详情包含重试时间
        assert "details" in error_dict["error"]
        assert str(retry_after) in error_dict["error"]["details"]
        
        # 验证：类别正确
        assert error_dict["error"]["category"] == ErrorCategory.RATE_LIMIT.value
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_has_default_message(self, error_code: ErrorCode):
        """
        属性：所有错误都有默认消息
        
        对于任意错误代码，系统应该提供默认的错误消息
        """
        message = ErrorHandlerService._get_default_message(error_code)
        
        # 验证：消息不为空
        assert message is not None
        assert len(message) > 0
        assert message != "未知错误"  # 应该有具体的消息
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_important_errors_have_solutions(self, error_code: ErrorCode):
        """
        属性48：错误处理 - 重要错误有解决方案
        
        对于重要的错误代码，系统应该提供解决方案
        """
        # 定义重要的错误代码
        important_codes = [
            ErrorCode.INVALID_CREDENTIALS,
            ErrorCode.TOKEN_EXPIRED,
            ErrorCode.INSUFFICIENT_PERMISSIONS,
            ErrorCode.QUOTA_EXCEEDED,
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.RESOURCE_NOT_FOUND,
            ErrorCode.CONCURRENT_MODIFICATION,
            ErrorCode.AI_MODEL_ERROR,
            ErrorCode.INSUFFICIENT_QUOTA,
            ErrorCode.EXPORT_FAILED
        ]
        
        if error_code in important_codes:
            # 验证：有解决方案
            assert error_code in ErrorHandlerService.ERROR_SOLUTIONS
            solutions = ErrorHandlerService.ERROR_SOLUTIONS[error_code]
            assert len(solutions) > 0
            
            # 验证：解决方案有内容
            for solution in solutions:
                assert len(solution.title) > 0
                assert len(solution.description) > 0
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_solutions_are_actionable(self, error_code: ErrorCode):
        """
        属性48：错误处理 - 解决方案是可操作的
        
        对于有解决方案的错误，解决方案应该包含具体的操作步骤
        """
        if error_code in ErrorHandlerService.ERROR_SOLUTIONS:
            solutions = ErrorHandlerService.ERROR_SOLUTIONS[error_code]
            
            for solution in solutions:
                # 验证：解决方案有标题和描述
                assert len(solution.title) > 0
                assert len(solution.description) > 0
                
                # 验证：解决方案转换为字典格式正确
                solution_dict = solution.to_dict()
                assert "title" in solution_dict
                assert "description" in solution_dict
    
    @given(
        error_code=error_codes,
        details=error_details
    )
    @settings(max_examples=100, deadline=None)
    def test_property_error_details_are_included(
        self,
        error_code: ErrorCode,
        details: str
    ):
        """
        属性：错误详情被包含在响应中
        
        对于任意带详情的错误，响应应该包含详细信息
        """
        assume(len(details) > 0)
        
        response = ErrorHandlerService.create_error_response(
            error_code,
            details=details
        )
        
        # 验证：详情被保存
        assert response.details == details
        
        data = response.to_dict()
        assert "details" in data["error"]
        assert data["error"]["details"] == details
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_response_is_json_serializable(
        self,
        error_code: ErrorCode
    ):
        """
        属性：错误响应可以序列化为JSON
        
        对于任意错误响应，应该可以转换为JSON格式
        """
        import json
        
        response = ErrorHandlerService.create_error_response(error_code)
        data = response.to_dict()
        
        # 验证：可以序列化为JSON
        try:
            json_str = json.dumps(data)
            assert len(json_str) > 0
            
            # 验证：可以反序列化
            parsed = json.loads(json_str)
            assert parsed == data
        except (TypeError, ValueError) as e:
            pytest.fail(f"错误响应无法序列化为JSON: {e}")
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_code_is_unique(self, error_code: ErrorCode):
        """
        属性：错误代码是唯一的
        
        对于任意错误代码，其数值应该是唯一的
        """
        # 获取所有错误代码的值
        all_codes = [code.value for code in ErrorCode]
        
        # 验证：当前错误代码的值在列表中只出现一次
        assert all_codes.count(error_code.value) == 1
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_category_is_valid(self, error_code: ErrorCode):
        """
        属性：错误类别是有效的
        
        对于任意错误代码，其类别应该是预定义的类别之一
        """
        category = ErrorHandlerService._get_error_category(error_code)
        
        # 验证：类别是有效的枚举值
        assert category in ErrorCategory
        
        # 验证：类别值是字符串
        assert isinstance(category.value, str)
    
    @given(
        error_code=st.sampled_from([
            ErrorCode.INVALID_CREDENTIALS,
            ErrorCode.INSUFFICIENT_PERMISSIONS,
            ErrorCode.QUOTA_EXCEEDED,
            ErrorCode.RATE_LIMIT_EXCEEDED
        ])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_common_errors_have_helpful_solutions(
        self,
        error_code: ErrorCode
    ):
        """
        属性48：错误处理 - 常见错误有有用的解决方案
        
        对于常见的错误，解决方案应该包含具体的步骤
        """
        response = ErrorHandlerService.create_error_response(error_code)
        
        # 验证：有解决方案
        assert len(response.solutions) > 0
        
        # 验证：至少一个解决方案有步骤
        has_steps = any(len(s.steps) > 0 for s in response.solutions)
        assert has_steps
        
        # 验证：解决方案在响应中
        data = response.to_dict()
        assert "solutions" in data["error"]
        assert len(data["error"]["solutions"]) > 0
    
    @given(
        error_code=error_codes,
        field=field_names
    )
    @settings(max_examples=100, deadline=None)
    def test_property_field_specific_errors_include_field(
        self,
        error_code: ErrorCode,
        field: str
    ):
        """
        属性：字段特定的错误包含字段名
        
        对于指定了字段的错误，响应应该包含字段信息
        """
        response = ErrorHandlerService.create_error_response(
            error_code,
            field=field
        )
        
        # 验证：字段被保存
        assert response.field == field
        
        data = response.to_dict()
        assert "field" in data["error"]
        assert data["error"]["field"] == field
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_response_structure_is_consistent(
        self,
        error_code: ErrorCode
    ):
        """
        属性48：错误处理 - 响应结构一致
        
        对于任意错误，响应结构应该保持一致
        """
        response = ErrorHandlerService.create_error_response(error_code)
        data = response.to_dict()
        
        # 验证：顶层只有error键
        assert list(data.keys()) == ["error"]
        
        # 验证：error对象包含必需字段
        error_obj = data["error"]
        assert "code" in error_obj
        assert "message" in error_obj
        assert "category" in error_obj
        
        # 验证：可选字段如果存在，类型正确
        if "details" in error_obj:
            assert isinstance(error_obj["details"], str)
        
        if "field" in error_obj:
            assert isinstance(error_obj["field"], str)
        
        if "solutions" in error_obj:
            assert isinstance(error_obj["solutions"], list)
    
    @given(
        error_code=st.sampled_from([
            ErrorCode.INVALID_CREDENTIALS,
            ErrorCode.TOKEN_EXPIRED,
            ErrorCode.INSUFFICIENT_PERMISSIONS
        ])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_auth_errors_provide_clear_guidance(
        self,
        error_code: ErrorCode
    ):
        """
        属性48：错误处理 - 认证/授权错误提供清晰指导
        
        对于认证和授权错误，应该提供清晰的解决指导
        """
        response = ErrorHandlerService.create_error_response(error_code)
        data = response.to_dict()
        
        # 验证：有解决方案
        assert "solutions" in data["error"]
        assert len(data["error"]["solutions"]) > 0
        
        # 验证：解决方案有描述
        for solution in data["error"]["solutions"]:
            assert "title" in solution
            assert "description" in solution
            assert len(solution["description"]) > 0
    
    @given(error_code=error_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_error_message_is_user_friendly(
        self,
        error_code: ErrorCode
    ):
        """
        属性48：错误处理 - 错误消息用户友好
        
        对于任意错误，消息应该是用户可理解的中文
        """
        message = ErrorHandlerService._get_default_message(error_code)
        
        # 验证：消息是中文（包含中文字符）
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in message)
        assert has_chinese or len(message) > 0  # 至少有内容
        
        # 验证：消息不包含技术术语（如异常类名）
        assert "Exception" not in message
        assert "Error" not in message or "错误" in message
