"""异步任务处理"""
import asyncio
import functools
from typing import Any, Callable, Dict, Optional
from datetime import datetime
from enum import Enum
import uuid


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AsyncTask:
    """异步任务"""
    
    def __init__(
        self,
        task_id: str,
        func: Callable,
        *args,
        **kwargs
    ):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self._task: Optional[asyncio.Task] = None
    
    async def execute(self) -> Any:
        """执行任务"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
        
        try:
            # 执行函数
            if asyncio.iscoroutinefunction(self.func):
                self.result = await self.func(*self.args, **self.kwargs)
            else:
                self.result = self.func(*self.args, **self.kwargs)
            
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            return self.result
        
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.completed_at = datetime.utcnow()
            raise
    
    def cancel(self) -> bool:
        """取消任务"""
        if self._task and not self._task.done():
            self._task.cancel()
            self.status = TaskStatus.CANCELLED
            self.completed_at = datetime.utcnow()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, AsyncTask] = {}
        self._background_tasks: set = set()
    
    def create_task(
        self,
        func: Callable,
        *args,
        task_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        创建异步任务
        
        参数:
            func: 要执行的函数
            *args: 位置参数
            task_id: 任务ID（可选，默认生成UUID）
            **kwargs: 关键字参数
        
        返回:
            任务ID
        """
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        task = AsyncTask(task_id, func, *args, **kwargs)
        self.tasks[task_id] = task
        
        # 创建后台任务
        asyncio_task = asyncio.create_task(self._run_task(task))
        task._task = asyncio_task
        self._background_tasks.add(asyncio_task)
        asyncio_task.add_done_callback(self._background_tasks.discard)
        
        return task_id
    
    async def _run_task(self, task: AsyncTask) -> None:
        """运行任务"""
        try:
            await task.execute()
        except Exception:
            # 错误已在task.execute()中记录
            pass
    
    def get_task(self, task_id: str) -> Optional[AsyncTask]:
        """
        获取任务
        
        参数:
            task_id: 任务ID
        
        返回:
            任务对象，如果不存在则返回None
        """
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        参数:
            task_id: 任务ID
        
        返回:
            任务状态字典，如果不存在则返回None
        """
        task = self.get_task(task_id)
        if task:
            return task.to_dict()
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        参数:
            task_id: 任务ID
        
        返回:
            是否成功取消
        """
        task = self.get_task(task_id)
        if task:
            return task.cancel()
        return False
    
    def cleanup_completed_tasks(self, max_age_seconds: int = 3600) -> int:
        """
        清理已完成的任务
        
        参数:
            max_age_seconds: 最大保留时间（秒）
        
        返回:
            清理的任务数量
        """
        now = datetime.utcnow()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                if task.completed_at:
                    age = (now - task.completed_at).total_seconds()
                    if age > max_age_seconds:
                        to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
        
        return len(to_remove)


# 全局任务管理器实例
task_manager = AsyncTaskManager()


def background_task(func: Callable) -> Callable:
    """
    后台任务装饰器
    
    用法:
        @background_task
        async def process_video(project_id: str):
            ...
        
        # 调用时会返回任务ID
        task_id = await process_video(project_id="123")
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        task_id = task_manager.create_task(func, *args, **kwargs)
        return task_id
    
    return wrapper
