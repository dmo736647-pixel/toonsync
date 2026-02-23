"""Redis缓存管理"""
import json
from typing import Any, Optional
import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings


class CacheManager:
    """Redis缓存管理器"""
    
    def __init__(self) -> None:
        self._redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        """连接到Redis"""
        self._redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    
    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self._redis:
            await self._redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        从缓存获取值
        
        参数:
            key: 缓存键
        
        返回:
            缓存的值，如果不存在则返回None
        """
        if not self._redis:
            return None
        
        value = await self._redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        设置缓存值
        
        参数:
            key: 缓存键
            value: 要缓存的值
            expire: 过期时间（秒），None表示永不过期
        
        返回:
            是否设置成功
        """
        if not self._redis:
            return False
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        if expire:
            await self._redis.setex(key, expire, value)
        else:
            await self._redis.set(key, value)
        
        return True
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存
        
        参数:
            key: 缓存键
        
        返回:
            是否删除成功
        """
        if not self._redis:
            return False
        
        await self._redis.delete(key)
        return True
    
    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        参数:
            key: 缓存键
        
        返回:
            是否存在
        """
        if not self._redis:
            return False
        
        return bool(await self._redis.exists(key))


# 全局缓存管理器实例
cache_manager = CacheManager()


async def get_cache() -> CacheManager:
    """获取缓存管理器的依赖注入函数"""
    return cache_manager
