"""错误处理服务测试"""
import pytest

from app.services.error_handler import (
    ErrorCode,
    ErrorCategory,
    ErrorSolution,
    ErrorResponse,
    ErrorHandlerService
)


class TestErrorSolution:
    """错误解决方案测试"""
    
    def test_create_error_solution(self):
        """测试创建错误解决方案"""
        solution = ErrorSolution(
            "重新登录",
            "您的登录会话已过期",
            ["点击登录按钮", "输入凭证"],
            "/docs/auth"
        )
        
        assert solution.title == "重新登录"
        assert solution.description == "您的登录会话已过期"
        assert len(solution.steps) == 2
        assert solution.documentation_url == "/docs/auth"
    
    def test_solution_to_dict(self):
        """测试解决方案转换为字典"""
        solution = ErrorSolution(
            "重新登录",
            "您的登录会话已过期",
            ["点击登录按钮"],
            "/docs/auth"
        )
        
        data = solution.to_dict()
        
        assert data["title"] == "重新登录"
        assert data["description"] == "您的登录会话已过期"
        assert "steps" in data
        assert "documentation_url" in data


class TestErrorResponse:
    """错误响应测试"""
    
    def test_create_error_response(self):
        """测试创建错误响应"""
        response = ErrorResponse(
            ErrorCode.INVALID_CREDENTIALS,
            "用户名或密码错误",
            ErrorCategory.AUTHENTICATION
        )
        
        assert response.error_code == ErrorCode.INVALID_CREDENTIALS
        assert response.message == "用户名或密码错误"
        assert response.category == ErrorCategory.AUTHENTICATION
    
    def test_error_response_with_details(self):
        """测试带详细信息的错误响应"""
        response = ErrorResponse(
            ErrorCode.INVALID_INPUT,
            "输入无效",
            ErrorCategory.VALIDATION,
            details="字段 'email' 格式不正确",
            field="email"
        )
        
        assert response.details == "字段 'email' 格式不正确"
        assert response.field == "email"
    
    def test_error_response_with_solutions(self):
        """测试带解决方案的错误响应"""
        solution = ErrorSolution("重试", "请稍后重试")
        response = ErrorResponse(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            "请求过于频繁",
            ErrorCategory.RATE_LIMIT,
            solutions=[solution]
        )
        
        assert len(response.solutions) == 1
        assert response.solutions[0].title == "重试"
    
    def test_response_to_dict(self):
        """测试响应转换为字典"""
        solution = ErrorSolution("重试", "请稍后重试")
        response = ErrorResponse(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            "请求过于频繁",
            ErrorCategory.RATE_LIMIT,
            details="每分钟最多10次请求",
            solutions=[solution]
        )
        
        data = response.to_dict()
        
        assert "error" in data
        assert data["error"]["code"] == ErrorCode.RATE_LIMIT_EXCEEDED.value
        assert data["error"]["message"] == "请求过于频繁"
        assert data["error"]["category"] == "rate_limit"
        assert "details" in data["error"]
        assert "solutions" in data["error"]


class TestErrorHandlerService:
    """错误处理服务测试"""
    
    def test_get_error_category(self):
        """测试获取错误类别"""
        # 验证错误
        assert ErrorHandlerService._get_error_category(ErrorCode.INVALID_INPUT) == ErrorCategory.VALIDATION
        
        # 认证错误
        assert ErrorHandlerService._get_error_category(ErrorCode.INVALID_CREDENTIALS) == ErrorCategory.AUTHENTICATION
        
        # 授权错误
        assert ErrorHandlerService._get_error_category(ErrorCode.INSUFFICIENT_PERMISSIONS) == ErrorCategory.AUTHORIZATION
        
        # 资源未找到
        assert ErrorHandlerService._get_error_category(ErrorCode.RESOURCE_NOT_FOUND) == ErrorCategory.NOT_FOUND
        
        # 冲突错误
        assert ErrorHandlerService._get_error_category(ErrorCode.RESOURCE_ALREADY_EXISTS) == ErrorCategory.CONFLICT
        
        # 速率限制
        assert ErrorHandlerService._get_error_category(ErrorCode.RATE_LIMIT_EXCEEDED) == ErrorCategory.RATE_LIMIT
        
        # 服务器错误
        assert ErrorHandlerService._get_error_category(ErrorCode.INTERNAL_ERROR) == ErrorCategory.SERVER_ERROR
        
        # 外部服务错误
        assert ErrorHandlerService._get_error_category(ErrorCode.AI_MODEL_ERROR) == ErrorCategory.EXTERNAL_SERVICE
        
        # 业务逻辑错误
        assert ErrorHandlerService._get_error_category(ErrorCode.INSUFFICIENT_QUOTA) == ErrorCategory.BUSINESS_LOGIC
    
    def test_get_default_message(self):
        """测试获取默认错误消息"""
        message = ErrorHandlerService._get_default_message(ErrorCode.INVALID_CREDENTIALS)
        assert message == "用户名或密码错误"
        
        message = ErrorHandlerService._get_default_message(ErrorCode.RATE_LIMIT_EXCEEDED)
        assert message == "请求过于频繁"
    
    def test_create_error_response(self):
        """测试创建错误响应"""
        response = ErrorHandlerService.create_error_response(
            ErrorCode.INVALID_CREDENTIALS
        )
        
        assert response.error_code == ErrorCode.INVALID_CREDENTIALS
        assert response.category == ErrorCategory.AUTHENTICATION
        assert len(response.solutions) > 0
    
    def test_create_error_response_with_custom_message(self):
        """测试创建带自定义消息的错误响应"""
        response = ErrorHandlerService.create_error_response(
            ErrorCode.INVALID_CREDENTIALS,
            message="自定义错误消息"
        )
        
        assert response.message == "自定义错误消息"
    
    def test_create_error_response_with_details(self):
        """测试创建带详细信息的错误响应"""
        response = ErrorHandlerService.create_error_response(
            ErrorCode.INVALID_INPUT,
            details="字段验证失败"
        )
        
        assert response.details == "字段验证失败"
    
    def test_format_validation_error(self):
        """测试格式化验证错误"""
        error_dict = ErrorHandlerService.format_validation_error(
            "email",
            "邮箱格式不正确",
            "invalid@"
        )
        
        assert "error" in error_dict
        assert error_dict["error"]["field"] == "email"
        assert error_dict["error"]["category"] == "validation"
    
    def test_format_authentication_error(self):
        """测试格式化认证错误"""
        error_dict = ErrorHandlerService.format_authentication_error()
        
        assert "error" in error_dict
        assert error_dict["error"]["category"] == "authentication"
        assert len(error_dict["error"]["solutions"]) > 0
    
    def test_format_authorization_error(self):
        """测试格式化授权错误"""
        error_dict = ErrorHandlerService.format_authorization_error("admin")
        
        assert "error" in error_dict
        assert error_dict["error"]["category"] == "authorization"
        assert "admin" in error_dict["error"]["details"]
    
    def test_format_not_found_error(self):
        """测试格式化资源未找到错误"""
        error_dict = ErrorHandlerService.format_not_found_error("项目", "123")
        
        assert "error" in error_dict
        assert error_dict["error"]["category"] == "not_found"
        assert "项目" in error_dict["error"]["message"]
        assert "123" in error_dict["error"]["details"]
    
    def test_format_rate_limit_error(self):
        """测试格式化速率限制错误"""
        error_dict = ErrorHandlerService.format_rate_limit_error(60)
        
        assert "error" in error_dict
        assert error_dict["error"]["category"] == "rate_limit"
        assert "60" in error_dict["error"]["details"]
    
    def test_error_solutions_exist(self):
        """测试错误解决方案存在"""
        # 验证关键错误代码都有解决方案
        important_codes = [
            ErrorCode.INVALID_CREDENTIALS,
            ErrorCode.TOKEN_EXPIRED,
            ErrorCode.INSUFFICIENT_PERMISSIONS,
            ErrorCode.QUOTA_EXCEEDED,
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.RESOURCE_NOT_FOUND,
            ErrorCode.AI_MODEL_ERROR,
            ErrorCode.INSUFFICIENT_QUOTA,
            ErrorCode.EXPORT_FAILED
        ]
        
        for code in important_codes:
            assert code in ErrorHandlerService.ERROR_SOLUTIONS
            assert len(ErrorHandlerService.ERROR_SOLUTIONS[code]) > 0
    
    def test_error_solution_has_steps(self):
        """测试错误解决方案包含步骤"""
        solutions = ErrorHandlerService.ERROR_SOLUTIONS[ErrorCode.INVALID_CREDENTIALS]
        
        assert len(solutions) > 0
        assert len(solutions[0].steps) > 0
    
    def test_error_code_ranges(self):
        """测试错误代码范围"""
        # 验证错误
        assert 1000 <= ErrorCode.INVALID_INPUT.value < 2000
        
        # 认证错误
        assert 2000 <= ErrorCode.INVALID_CREDENTIALS.value < 3000
        
        # 授权错误
        assert 3000 <= ErrorCode.INSUFFICIENT_PERMISSIONS.value < 4000
        
        # 资源未找到
        assert 4000 <= ErrorCode.RESOURCE_NOT_FOUND.value < 5000
        
        # 冲突错误
        assert 5000 <= ErrorCode.RESOURCE_ALREADY_EXISTS.value < 6000
        
        # 速率限制
        assert 6000 <= ErrorCode.RATE_LIMIT_EXCEEDED.value < 7000
        
        # 服务器错误
        assert 7000 <= ErrorCode.INTERNAL_ERROR.value < 8000
        
        # 外部服务错误
        assert 8000 <= ErrorCode.AI_MODEL_ERROR.value < 9000
        
        # 业务逻辑错误
        assert 9000 <= ErrorCode.INSUFFICIENT_QUOTA.value < 10000
