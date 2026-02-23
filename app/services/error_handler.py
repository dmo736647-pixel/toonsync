"""错误处理服务"""
from typing import Dict, Optional, List
from enum import Enum


class ErrorCategory(Enum):
    """错误类别"""
    VALIDATION = "validation"  # 验证错误
    AUTHENTICATION = "authentication"  # 认证错误
    AUTHORIZATION = "authorization"  # 授权错误
    NOT_FOUND = "not_found"  # 资源未找到
    CONFLICT = "conflict"  # 冲突错误
    RATE_LIMIT = "rate_limit"  # 速率限制
    SERVER_ERROR = "server_error"  # 服务器错误
    EXTERNAL_SERVICE = "external_service"  # 外部服务错误
    BUSINESS_LOGIC = "business_logic"  # 业务逻辑错误


class ErrorCode(Enum):
    """错误代码"""
    # 验证错误 (1000-1999)
    INVALID_INPUT = 1000
    MISSING_FIELD = 1001
    INVALID_FORMAT = 1002
    INVALID_VALUE = 1003
    
    # 认证错误 (2000-2999)
    INVALID_CREDENTIALS = 2000
    TOKEN_EXPIRED = 2001
    TOKEN_INVALID = 2002
    USER_NOT_FOUND = 2003
    
    # 授权错误 (3000-3999)
    INSUFFICIENT_PERMISSIONS = 3000
    SUBSCRIPTION_REQUIRED = 3001
    QUOTA_EXCEEDED = 3002
    FEATURE_NOT_AVAILABLE = 3003
    
    # 资源未找到 (4000-4999)
    RESOURCE_NOT_FOUND = 4000
    PROJECT_NOT_FOUND = 4001
    CHARACTER_NOT_FOUND = 4002
    ASSET_NOT_FOUND = 4003
    
    # 冲突错误 (5000-5999)
    RESOURCE_ALREADY_EXISTS = 5000
    CONCURRENT_MODIFICATION = 5001
    INVALID_STATE = 5002
    
    # 速率限制 (6000-6999)
    RATE_LIMIT_EXCEEDED = 6000
    TOO_MANY_REQUESTS = 6001
    
    # 服务器错误 (7000-7999)
    INTERNAL_ERROR = 7000
    DATABASE_ERROR = 7001
    CACHE_ERROR = 7002
    STORAGE_ERROR = 7003
    
    # 外部服务错误 (8000-8999)
    AI_MODEL_ERROR = 8000
    PAYMENT_SERVICE_ERROR = 8001
    EMAIL_SERVICE_ERROR = 8002
    
    # 业务逻辑错误 (9000-9999)
    INSUFFICIENT_QUOTA = 9000
    INVALID_WORKFLOW_STATE = 9001
    EXPORT_FAILED = 9002


class ErrorSolution:
    """错误解决方案"""
    
    def __init__(
        self,
        title: str,
        description: str,
        steps: Optional[List[str]] = None,
        documentation_url: Optional[str] = None
    ):
        self.title = title
        self.description = description
        self.steps = steps or []
        self.documentation_url = documentation_url
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "title": self.title,
            "description": self.description
        }
        if self.steps:
            result["steps"] = self.steps
        if self.documentation_url:
            result["documentation_url"] = self.documentation_url
        return result


class ErrorResponse:
    """错误响应"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        category: ErrorCategory,
        details: Optional[str] = None,
        field: Optional[str] = None,
        solutions: Optional[List[ErrorSolution]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.category = category
        self.details = details
        self.field = field
        self.solutions = solutions or []
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "category": self.category.value
            }
        }
        
        if self.details:
            result["error"]["details"] = self.details
        
        if self.field:
            result["error"]["field"] = self.field
        
        if self.solutions:
            result["error"]["solutions"] = [s.to_dict() for s in self.solutions]
        
        return result


class ErrorHandlerService:
    """错误处理服务"""
    
    # 错误代码到解决方案的映射
    ERROR_SOLUTIONS: Dict[ErrorCode, List[ErrorSolution]] = {
        ErrorCode.INVALID_CREDENTIALS: [
            ErrorSolution(
                "检查用户名和密码",
                "请确认您输入的用户名和密码是否正确",
                [
                    "检查是否开启了大写锁定",
                    "确认用户名拼写正确",
                    "尝试重置密码"
                ]
            )
        ],
        ErrorCode.TOKEN_EXPIRED: [
            ErrorSolution(
                "重新登录",
                "您的登录会话已过期，请重新登录",
                ["点击登录按钮", "输入您的凭证"]
            )
        ],
        ErrorCode.INSUFFICIENT_PERMISSIONS: [
            ErrorSolution(
                "升级订阅",
                "此功能需要更高级别的订阅",
                [
                    "查看订阅计划",
                    "选择合适的订阅级别",
                    "完成支付"
                ],
                "/docs/subscription"
            )
        ],
        ErrorCode.QUOTA_EXCEEDED: [
            ErrorSolution(
                "升级订阅或等待配额重置",
                "您已达到当前订阅的使用配额",
                [
                    "等待配额在下个计费周期重置",
                    "或升级到更高级别的订阅"
                ],
                "/docs/quota"
            )
        ],
        ErrorCode.RATE_LIMIT_EXCEEDED: [
            ErrorSolution(
                "稍后重试",
                "您的请求过于频繁，请稍后再试",
                ["等待几分钟后重试", "减少请求频率"]
            )
        ],
        ErrorCode.RESOURCE_NOT_FOUND: [
            ErrorSolution(
                "检查资源ID",
                "请求的资源不存在或已被删除",
                [
                    "确认资源ID是否正确",
                    "检查资源是否已被删除",
                    "刷新页面重新加载"
                ]
            )
        ],
        ErrorCode.CONCURRENT_MODIFICATION: [
            ErrorSolution(
                "刷新并重试",
                "资源已被其他用户修改",
                [
                    "刷新页面获取最新数据",
                    "重新进行修改操作"
                ]
            )
        ],
        ErrorCode.AI_MODEL_ERROR: [
            ErrorSolution(
                "重试或联系支持",
                "AI模型处理失败",
                [
                    "稍后重试",
                    "如果问题持续，请联系技术支持"
                ],
                "/docs/support"
            )
        ],
        ErrorCode.INSUFFICIENT_QUOTA: [
            ErrorSolution(
                "充值或升级",
                "您的账户余额不足",
                [
                    "充值账户",
                    "或升级到包含更多配额的订阅计划"
                ],
                "/docs/billing"
            )
        ],
        ErrorCode.EXPORT_FAILED: [
            ErrorSolution(
                "检查项目并重试",
                "视频导出失败",
                [
                    "确认项目所有必需的资源都已上传",
                    "检查项目设置是否正确",
                    "重新尝试导出"
                ],
                "/docs/export"
            )
        ]
    }
    
    @classmethod
    def create_error_response(
        cls,
        error_code: ErrorCode,
        message: Optional[str] = None,
        details: Optional[str] = None,
        field: Optional[str] = None
    ) -> ErrorResponse:
        """创建错误响应"""
        # 确定错误类别
        category = cls._get_error_category(error_code)
        
        # 使用默认消息或自定义消息
        if message is None:
            message = cls._get_default_message(error_code)
        
        # 获取解决方案
        solutions = cls.ERROR_SOLUTIONS.get(error_code, [])
        
        return ErrorResponse(
            error_code=error_code,
            message=message,
            category=category,
            details=details,
            field=field,
            solutions=solutions
        )
    
    @staticmethod
    def _get_error_category(error_code: ErrorCode) -> ErrorCategory:
        """根据错误代码获取错误类别"""
        code_value = error_code.value
        
        if 1000 <= code_value < 2000:
            return ErrorCategory.VALIDATION
        elif 2000 <= code_value < 3000:
            return ErrorCategory.AUTHENTICATION
        elif 3000 <= code_value < 4000:
            return ErrorCategory.AUTHORIZATION
        elif 4000 <= code_value < 5000:
            return ErrorCategory.NOT_FOUND
        elif 5000 <= code_value < 6000:
            return ErrorCategory.CONFLICT
        elif 6000 <= code_value < 7000:
            return ErrorCategory.RATE_LIMIT
        elif 7000 <= code_value < 8000:
            return ErrorCategory.SERVER_ERROR
        elif 8000 <= code_value < 9000:
            return ErrorCategory.EXTERNAL_SERVICE
        else:
            return ErrorCategory.BUSINESS_LOGIC
    
    @staticmethod
    def _get_default_message(error_code: ErrorCode) -> str:
        """获取默认错误消息"""
        messages = {
            ErrorCode.INVALID_INPUT: "输入数据无效",
            ErrorCode.MISSING_FIELD: "缺少必需字段",
            ErrorCode.INVALID_FORMAT: "数据格式不正确",
            ErrorCode.INVALID_VALUE: "字段值无效",
            
            ErrorCode.INVALID_CREDENTIALS: "用户名或密码错误",
            ErrorCode.TOKEN_EXPIRED: "登录会话已过期",
            ErrorCode.TOKEN_INVALID: "无效的访问令牌",
            ErrorCode.USER_NOT_FOUND: "用户不存在",
            
            ErrorCode.INSUFFICIENT_PERMISSIONS: "权限不足",
            ErrorCode.SUBSCRIPTION_REQUIRED: "需要订阅才能访问此功能",
            ErrorCode.QUOTA_EXCEEDED: "已超出使用配额",
            ErrorCode.FEATURE_NOT_AVAILABLE: "功能不可用",
            
            ErrorCode.RESOURCE_NOT_FOUND: "资源未找到",
            ErrorCode.PROJECT_NOT_FOUND: "项目不存在",
            ErrorCode.CHARACTER_NOT_FOUND: "角色不存在",
            ErrorCode.ASSET_NOT_FOUND: "素材不存在",
            
            ErrorCode.RESOURCE_ALREADY_EXISTS: "资源已存在",
            ErrorCode.CONCURRENT_MODIFICATION: "资源已被其他用户修改",
            ErrorCode.INVALID_STATE: "资源状态无效",
            
            ErrorCode.RATE_LIMIT_EXCEEDED: "请求过于频繁",
            ErrorCode.TOO_MANY_REQUESTS: "请求次数过多",
            
            ErrorCode.INTERNAL_ERROR: "服务器内部错误",
            ErrorCode.DATABASE_ERROR: "数据库错误",
            ErrorCode.CACHE_ERROR: "缓存错误",
            ErrorCode.STORAGE_ERROR: "存储错误",
            
            ErrorCode.AI_MODEL_ERROR: "AI模型处理失败",
            ErrorCode.PAYMENT_SERVICE_ERROR: "支付服务错误",
            ErrorCode.EMAIL_SERVICE_ERROR: "邮件服务错误",
            
            ErrorCode.INSUFFICIENT_QUOTA: "余额不足",
            ErrorCode.INVALID_WORKFLOW_STATE: "工作流状态无效",
            ErrorCode.EXPORT_FAILED: "导出失败"
        }
        
        return messages.get(error_code, "未知错误")
    
    @classmethod
    def format_validation_error(
        cls,
        field: str,
        message: str,
        value: Optional[str] = None
    ) -> Dict:
        """格式化验证错误"""
        details = f"字段 '{field}' 验证失败"
        if value:
            details += f": {value}"
        
        error_response = cls.create_error_response(
            ErrorCode.INVALID_INPUT,
            message=message,
            details=details,
            field=field
        )
        
        return error_response.to_dict()
    
    @classmethod
    def format_authentication_error(cls, message: Optional[str] = None) -> Dict:
        """格式化认证错误"""
        error_response = cls.create_error_response(
            ErrorCode.INVALID_CREDENTIALS,
            message=message
        )
        return error_response.to_dict()
    
    @classmethod
    def format_authorization_error(
        cls,
        required_permission: Optional[str] = None
    ) -> Dict:
        """格式化授权错误"""
        details = None
        if required_permission:
            details = f"需要权限: {required_permission}"
        
        error_response = cls.create_error_response(
            ErrorCode.INSUFFICIENT_PERMISSIONS,
            details=details
        )
        return error_response.to_dict()
    
    @classmethod
    def format_not_found_error(
        cls,
        resource_type: str,
        resource_id: Optional[str] = None
    ) -> Dict:
        """格式化资源未找到错误"""
        message = f"{resource_type}不存在"
        details = None
        if resource_id:
            details = f"ID: {resource_id}"
        
        error_response = cls.create_error_response(
            ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            details=details
        )
        return error_response.to_dict()
    
    @classmethod
    def format_rate_limit_error(cls, retry_after: Optional[int] = None) -> Dict:
        """格式化速率限制错误"""
        details = None
        if retry_after:
            details = f"请在 {retry_after} 秒后重试"
        
        error_response = cls.create_error_response(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            details=details
        )
        return error_response.to_dict()


# 全局错误处理服务实例
error_handler_service = ErrorHandlerService()
