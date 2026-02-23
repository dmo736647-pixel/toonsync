"""性能优化服务"""
import functools
import hashlib
import json
from typing import Any, Callable, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Index

from app.core.cache import cache_manager


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.cache_ttl = {
            "user": 300,  # 5分钟
            "project": 180,  # 3分钟
            "character": 300,  # 5分钟
            "asset": 600,  # 10分钟
            "sound_effect": 3600,  # 1小时
        }
    
    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        生成缓存键
        
        参数:
            prefix: 缓存键前缀
            *args: 位置参数
            **kwargs: 关键字参数
        
        返回:
            缓存键字符串
        """
        # 将参数序列化为字符串
        key_parts = [prefix]
        
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}:{v}")
            else:
                key_parts.append(f"{k}:{hashlib.md5(str(v).encode()).hexdigest()[:8]}")
        
        return ":".join(key_parts)
    
    def cached(
        self,
        prefix: str,
        ttl: Optional[int] = None
    ) -> Callable:
        """
        缓存装饰器
        
        参数:
            prefix: 缓存键前缀
            ttl: 过期时间（秒），None使用默认值
        
        用法:
            @performance_optimizer.cached("user", ttl=300)
            async def get_user(user_id: str):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self.cache_key(prefix, *args, **kwargs)
                
                # 尝试从缓存获取
                cached_value = await cache_manager.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 存入缓存
                expire_time = ttl if ttl is not None else self.cache_ttl.get(prefix, 300)
                await cache_manager.set(cache_key, result, expire=expire_time)
                
                return result
            
            return wrapper
        return decorator
    
    async def invalidate_cache(self, prefix: str, *args, **kwargs) -> bool:
        """
        使缓存失效
        
        参数:
            prefix: 缓存键前缀
            *args: 位置参数
            **kwargs: 关键字参数
        
        返回:
            是否成功
        """
        cache_key = self.cache_key(prefix, *args, **kwargs)
        return await cache_manager.delete(cache_key)


class DatabaseOptimizer:
    """数据库查询优化器"""
    
    @staticmethod
    def add_indexes(db: Session) -> None:
        """
        添加数据库索引以优化查询性能
        
        参数:
            db: 数据库会话
        """
        from app.models.user import User
        from app.models.project import Project
        from app.models.character import Character
        from app.models.storyboard import StoryboardFrame
        from app.models.asset import Asset
        from app.models.sound_effect import SoundEffect
        from app.models.collaboration import ProjectCollaborator
        
        # 用户表索引
        Index('idx_users_email', User.email, unique=True)
        Index('idx_users_subscription_tier', User.subscription_tier)
        
        # 项目表索引
        Index('idx_projects_user_id', Project.user_id)
        Index('idx_projects_created_at', Project.created_at)
        Index('idx_projects_user_created', Project.user_id, Project.created_at)
        
        # 角色表索引
        Index('idx_characters_project_id', Character.project_id)
        
        # 分镜表索引
        Index('idx_storyboard_project_id', StoryboardFrame.project_id)
        Index('idx_storyboard_sequence', StoryboardFrame.project_id, StoryboardFrame.sequence_number)
        
        # 素材表索引
        Index('idx_assets_user_id', Asset.user_id)
        Index('idx_assets_type', Asset.asset_type)
        Index('idx_assets_user_type', Asset.user_id, Asset.asset_type)
        
        # 音效表索引
        Index('idx_sound_effects_category', SoundEffect.category)
        
        # 协作表索引
        Index('idx_collaborators_project', ProjectCollaborator.project_id)
        Index('idx_collaborators_user', ProjectCollaborator.user_id)
    
    @staticmethod
    def optimize_query_with_eager_loading(query, *relationships):
        """
        使用预加载优化查询，避免N+1问题
        
        参数:
            query: SQLAlchemy查询对象
            *relationships: 要预加载的关系
        
        返回:
            优化后的查询对象
        """
        from sqlalchemy.orm import joinedload
        
        for relationship in relationships:
            query = query.options(joinedload(relationship))
        
        return query
    
    @staticmethod
    def paginate_query(query, page: int = 1, page_size: int = 50):
        """
        分页查询
        
        参数:
            query: SQLAlchemy查询对象
            page: 页码（从1开始）
            page_size: 每页大小
        
        返回:
            分页后的查询结果和总数
        """
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }


# 全局性能优化器实例
performance_optimizer = PerformanceOptimizer()
database_optimizer = DatabaseOptimizer()
