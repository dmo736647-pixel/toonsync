"""用户操作隔离服务"""
import time
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio


class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        # 存储每个用户的请求记录：{user_id: [(timestamp, count)]}
        self.user_requests: Dict[str, list] = defaultdict(list)
        # 速率限制配置
        self.limits = {
            "default": (100, 60),  # 每分钟100个请求
            "api": (60, 60),       # API调用：每分钟60个
            "upload": (10, 60),    # 上传：每分钟10个
            "export": (5, 300),    # 导出：每5分钟5个
        }
    
    def check_rate_limit(
        self,
        user_id: str,
        limit_type: str = "default"
    ) -> tuple[bool, Optional[int]]:
        """
        检查速率限制
        
        参数:
            user_id: 用户ID
            limit_type: 限制类型
        
        返回:
            (是否允许, 剩余秒数)
        """
        if limit_type not in self.limits:
            limit_type = "default"
        
        max_requests, time_window = self.limits[limit_type]
        current_time = time.time()
        
        # 清理过期的请求记录
        self.user_requests[user_id] = [
            (ts, count) for ts, count in self.user_requests[user_id]
            if current_time - ts < time_window
        ]
        
        # 计算时间窗口内的请求总数
        total_requests = sum(count for _, count in self.user_requests[user_id])
        
        if total_requests >= max_requests:
            # 计算需要等待的时间
            oldest_request = min(ts for ts, _ in self.user_requests[user_id])
            wait_time = int(time_window - (current_time - oldest_request)) + 1
            return False, wait_time
        
        # 记录本次请求
        self.user_requests[user_id].append((current_time, 1))
        return True, None
    
    def get_remaining_quota(self, user_id: str, limit_type: str = "default") -> int:
        """
        获取剩余配额
        
        参数:
            user_id: 用户ID
            limit_type: 限制类型
        
        返回:
            剩余请求数
        """
        if limit_type not in self.limits:
            limit_type = "default"
        
        max_requests, time_window = self.limits[limit_type]
        current_time = time.time()
        
        # 清理过期的请求记录
        self.user_requests[user_id] = [
            (ts, count) for ts, count in self.user_requests[user_id]
            if current_time - ts < time_window
        ]
        
        # 计算剩余配额
        total_requests = sum(count for _, count in self.user_requests[user_id])
        return max(0, max_requests - total_requests)


class ErrorIsolation:
    """错误隔离机制"""
    
    def __init__(self):
        # 存储每个用户的错误记录
        self.user_errors: Dict[str, list] = defaultdict(list)
        # 错误阈值配置
        self.error_threshold = 10  # 5分钟内最多10个错误
        self.time_window = 300  # 5分钟
    
    def record_error(self, user_id: str, error: Exception) -> None:
        """
        记录用户错误
        
        参数:
            user_id: 用户ID
            error: 错误对象
        """
        current_time = time.time()
        
        # 清理过期的错误记录
        self.user_errors[user_id] = [
            (ts, err) for ts, err in self.user_errors[user_id]
            if current_time - ts < self.time_window
        ]
        
        # 记录新错误
        self.user_errors[user_id].append((current_time, str(error)))
    
    def should_isolate(self, user_id: str) -> bool:
        """
        判断是否应该隔离用户
        
        参数:
            user_id: 用户ID
        
        返回:
            是否应该隔离
        """
        current_time = time.time()
        
        # 清理过期的错误记录
        self.user_errors[user_id] = [
            (ts, err) for ts, err in self.user_errors[user_id]
            if current_time - ts < self.time_window
        ]
        
        # 检查错误数量
        return len(self.user_errors[user_id]) >= self.error_threshold
    
    def get_error_count(self, user_id: str) -> int:
        """
        获取用户错误数量
        
        参数:
            user_id: 用户ID
        
        返回:
            错误数量
        """
        current_time = time.time()
        
        # 清理过期的错误记录
        self.user_errors[user_id] = [
            (ts, err) for ts, err in self.user_errors[user_id]
            if current_time - ts < self.time_window
        ]
        
        return len(self.user_errors[user_id])


class DataIsolation:
    """数据隔离机制（多租户）"""
    
    @staticmethod
    def add_user_filter(query, user_id: str, model_class):
        """
        为查询添加用户过滤条件
        
        参数:
            query: SQLAlchemy查询对象
            user_id: 用户ID
            model_class: 模型类
        
        返回:
            过滤后的查询对象
        """
        # 检查模型是否有user_id字段
        if hasattr(model_class, 'user_id'):
            return query.filter(model_class.user_id == user_id)
        return query
    
    @staticmethod
    def verify_ownership(resource, user_id: str) -> bool:
        """
        验证资源所有权
        
        参数:
            resource: 资源对象
            user_id: 用户ID
        
        返回:
            是否拥有资源
        """
        if hasattr(resource, 'user_id'):
            return resource.user_id == user_id
        return False
    
    @staticmethod
    def can_access(resource, user_id: str) -> bool:
        """
        检查用户是否可以访问资源
        
        参数:
            resource: 资源对象
            user_id: 用户ID
        
        返回:
            是否可以访问
        """
        # 检查所有权
        if DataIsolation.verify_ownership(resource, user_id):
            return True
        
        # 检查协作权限（如果资源支持协作）
        if hasattr(resource, 'collaborators'):
            for collab in resource.collaborators:
                if collab.user_id == user_id:
                    return True
        
        return False


class ResourceLimiter:
    """资源限制器"""
    
    def __init__(self):
        # 资源使用记录
        self.resource_usage: Dict[str, Dict] = defaultdict(lambda: {
            "cpu_time": 0.0,
            "memory": 0,
            "requests": 0,
            "last_reset": time.time()
        })
        
        # 资源限制配置
        self.limits = {
            "cpu_time": 300,      # 每小时最多300秒CPU时间
            "memory": 1024 * 1024 * 1024,  # 1GB内存
            "requests": 1000,     # 每小时1000个请求
        }
        
        self.reset_interval = 3600  # 1小时重置一次
    
    def check_resource_limit(
        self,
        user_id: str,
        resource_type: str,
        amount: float
    ) -> bool:
        """
        检查资源限制
        
        参数:
            user_id: 用户ID
            resource_type: 资源类型
            amount: 使用量
        
        返回:
            是否允许使用
        """
        current_time = time.time()
        usage = self.resource_usage[user_id]
        
        # 检查是否需要重置
        if current_time - usage["last_reset"] > self.reset_interval:
            usage["cpu_time"] = 0.0
            usage["memory"] = 0
            usage["requests"] = 0
            usage["last_reset"] = current_time
        
        # 检查限制
        if resource_type in self.limits:
            current_usage = usage.get(resource_type, 0)
            if current_usage + amount > self.limits[resource_type]:
                return False
        
        # 记录使用
        usage[resource_type] = usage.get(resource_type, 0) + amount
        return True
    
    def get_resource_usage(self, user_id: str) -> Dict:
        """
        获取资源使用情况
        
        参数:
            user_id: 用户ID
        
        返回:
            资源使用字典
        """
        current_time = time.time()
        usage = self.resource_usage[user_id]
        
        # 检查是否需要重置
        if current_time - usage["last_reset"] > self.reset_interval:
            usage["cpu_time"] = 0.0
            usage["memory"] = 0
            usage["requests"] = 0
            usage["last_reset"] = current_time
        
        return {
            "cpu_time": usage["cpu_time"],
            "memory": usage["memory"],
            "requests": usage["requests"],
            "limits": self.limits,
            "reset_in": int(self.reset_interval - (current_time - usage["last_reset"]))
        }


# 全局实例
rate_limiter = RateLimiter()
error_isolation = ErrorIsolation()
data_isolation = DataIsolation()
resource_limiter = ResourceLimiter()
