"""实时反馈服务"""
import asyncio
import json
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from enum import Enum


class ProgressStatus(Enum):
    """进度状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(Enum):
    """消息类型"""
    PROGRESS = "progress"
    STATUS = "status"
    ERROR = "error"
    SUCCESS = "success"
    INFO = "info"


class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, task_id: str, total_steps: int, description: str = ""):
        self.task_id = task_id
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.status = ProgressStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.step_descriptions: Dict[int, str] = {}
    
    def start(self):
        """开始任务"""
        self.status = ProgressStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
    
    def update(self, step: int, description: str = ""):
        """更新进度"""
        self.current_step = step
        if description:
            self.step_descriptions[step] = description
    
    def complete(self):
        """完成任务"""
        self.status = ProgressStatus.COMPLETED
        self.current_step = self.total_steps
        self.completed_at = datetime.utcnow()
    
    def fail(self, error_message: str):
        """任务失败"""
        self.status = ProgressStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
    
    def cancel(self):
        """取消任务"""
        self.status = ProgressStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    def get_percentage(self) -> float:
        """获取完成百分比"""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "percentage": self.get_percentage(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "current_step_description": self.step_descriptions.get(self.current_step, "")
        }


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 用户ID -> WebSocket连接集合
        self.active_connections: Dict[str, Set[Any]] = {}
        # 任务ID -> 进度跟踪器
        self.progress_trackers: Dict[str, ProgressTracker] = {}
    
    async def connect(self, websocket: Any, user_id: str):
        """连接WebSocket"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: Any, user_id: str):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: Dict, user_id: str):
        """发送个人消息"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # 清理断开的连接
            for connection in disconnected:
                self.disconnect(connection, user_id)
    
    async def broadcast(self, message: Dict):
        """广播消息给所有用户"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)
    
    def create_progress_tracker(
        self,
        task_id: str,
        total_steps: int,
        description: str = ""
    ) -> ProgressTracker:
        """创建进度跟踪器"""
        tracker = ProgressTracker(task_id, total_steps, description)
        self.progress_trackers[task_id] = tracker
        return tracker
    
    def get_progress_tracker(self, task_id: str) -> Optional[ProgressTracker]:
        """获取进度跟踪器"""
        return self.progress_trackers.get(task_id)
    
    async def send_progress_update(self, task_id: str, user_id: str):
        """发送进度更新"""
        tracker = self.get_progress_tracker(task_id)
        if tracker:
            message = {
                "type": MessageType.PROGRESS.value,
                "timestamp": datetime.utcnow().isoformat(),
                "data": tracker.to_dict()
            }
            await self.send_personal_message(message, user_id)
    
    async def send_status_message(
        self,
        user_id: str,
        status: str,
        message: str,
        data: Optional[Dict] = None
    ):
        """发送状态消息"""
        msg = {
            "type": MessageType.STATUS.value,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "message": message,
            "data": data or {}
        }
        await self.send_personal_message(msg, user_id)
    
    async def send_error_message(
        self,
        user_id: str,
        error: str,
        details: Optional[str] = None
    ):
        """发送错误消息"""
        msg = {
            "type": MessageType.ERROR.value,
            "timestamp": datetime.utcnow().isoformat(),
            "error": error,
            "details": details
        }
        await self.send_personal_message(msg, user_id)
    
    async def send_success_message(
        self,
        user_id: str,
        message: str,
        data: Optional[Dict] = None
    ):
        """发送成功消息"""
        msg = {
            "type": MessageType.SUCCESS.value,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "data": data or {}
        }
        await self.send_personal_message(msg, user_id)
    
    async def send_info_message(
        self,
        user_id: str,
        message: str,
        data: Optional[Dict] = None
    ):
        """发送信息消息"""
        msg = {
            "type": MessageType.INFO.value,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "data": data or {}
        }
        await self.send_personal_message(msg, user_id)
    
    def cleanup_old_trackers(self, max_age_hours: int = 24):
        """清理旧的进度跟踪器"""
        now = datetime.utcnow()
        to_remove = []
        
        for task_id, tracker in self.progress_trackers.items():
            if tracker.completed_at:
                age = (now - tracker.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.progress_trackers[task_id]


# 全局连接管理器实例
connection_manager = ConnectionManager()


class RealtimeFeedbackService:
    """实时反馈服务"""
    
    def __init__(self, manager: ConnectionManager = connection_manager):
        self.manager = manager
    
    async def start_task(
        self,
        task_id: str,
        user_id: str,
        total_steps: int,
        description: str = ""
    ) -> ProgressTracker:
        """开始任务并发送通知"""
        tracker = self.manager.create_progress_tracker(task_id, total_steps, description)
        tracker.start()
        
        await self.manager.send_status_message(
            user_id,
            "task_started",
            f"任务已开始: {description}",
            {"task_id": task_id}
        )
        
        await self.manager.send_progress_update(task_id, user_id)
        return tracker
    
    async def update_progress(
        self,
        task_id: str,
        user_id: str,
        step: int,
        description: str = ""
    ):
        """更新任务进度"""
        tracker = self.manager.get_progress_tracker(task_id)
        if tracker:
            tracker.update(step, description)
            await self.manager.send_progress_update(task_id, user_id)
    
    async def complete_task(
        self,
        task_id: str,
        user_id: str,
        result_data: Optional[Dict] = None
    ):
        """完成任务"""
        tracker = self.manager.get_progress_tracker(task_id)
        if tracker:
            tracker.complete()
            await self.manager.send_progress_update(task_id, user_id)
            await self.manager.send_success_message(
                user_id,
                f"任务完成: {tracker.description}",
                result_data
            )
    
    async def fail_task(
        self,
        task_id: str,
        user_id: str,
        error_message: str
    ):
        """任务失败"""
        tracker = self.manager.get_progress_tracker(task_id)
        if tracker:
            tracker.fail(error_message)
            await self.manager.send_progress_update(task_id, user_id)
            await self.manager.send_error_message(
                user_id,
                f"任务失败: {tracker.description}",
                error_message
            )
    
    async def cancel_task(
        self,
        task_id: str,
        user_id: str
    ):
        """取消任务"""
        tracker = self.manager.get_progress_tracker(task_id)
        if tracker:
            tracker.cancel()
            await self.manager.send_progress_update(task_id, user_id)
            await self.manager.send_info_message(
                user_id,
                f"任务已取消: {tracker.description}",
                {"task_id": task_id}
            )
    
    async def send_notification(
        self,
        user_id: str,
        message: str,
        notification_type: str = "info",
        data: Optional[Dict] = None
    ):
        """发送通知"""
        if notification_type == "error":
            await self.manager.send_error_message(user_id, message, data.get("details") if data else None)
        elif notification_type == "success":
            await self.manager.send_success_message(user_id, message, data)
        else:
            await self.manager.send_info_message(user_id, message, data)


# 全局实时反馈服务实例
realtime_feedback_service = RealtimeFeedbackService()
