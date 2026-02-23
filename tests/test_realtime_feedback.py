"""实时反馈服务测试"""
import pytest
import asyncio
from datetime import datetime

from app.services.realtime_feedback import (
    ProgressTracker,
    ProgressStatus,
    ConnectionManager,
    RealtimeFeedbackService,
    MessageType
)


class TestProgressTracker:
    """进度跟踪器测试"""
    
    def test_create_progress_tracker(self):
        """测试创建进度跟踪器"""
        tracker = ProgressTracker("task1", 10, "测试任务")
        
        assert tracker.task_id == "task1"
        assert tracker.total_steps == 10
        assert tracker.current_step == 0
        assert tracker.description == "测试任务"
        assert tracker.status == ProgressStatus.PENDING
    
    def test_start_task(self):
        """测试开始任务"""
        tracker = ProgressTracker("task1", 10)
        tracker.start()
        
        assert tracker.status == ProgressStatus.IN_PROGRESS
        assert tracker.started_at is not None
    
    def test_update_progress(self):
        """测试更新进度"""
        tracker = ProgressTracker("task1", 10)
        tracker.start()
        tracker.update(5, "处理中")
        
        assert tracker.current_step == 5
        assert tracker.step_descriptions[5] == "处理中"
        assert tracker.get_percentage() == 50.0
    
    def test_complete_task(self):
        """测试完成任务"""
        tracker = ProgressTracker("task1", 10)
        tracker.start()
        tracker.complete()
        
        assert tracker.status == ProgressStatus.COMPLETED
        assert tracker.current_step == 10
        assert tracker.completed_at is not None
    
    def test_fail_task(self):
        """测试任务失败"""
        tracker = ProgressTracker("task1", 10)
        tracker.start()
        tracker.fail("错误信息")
        
        assert tracker.status == ProgressStatus.FAILED
        assert tracker.error_message == "错误信息"
        assert tracker.completed_at is not None
    
    def test_cancel_task(self):
        """测试取消任务"""
        tracker = ProgressTracker("task1", 10)
        tracker.start()
        tracker.cancel()
        
        assert tracker.status == ProgressStatus.CANCELLED
        assert tracker.completed_at is not None
    
    def test_get_percentage(self):
        """测试获取完成百分比"""
        tracker = ProgressTracker("task1", 10)
        
        assert tracker.get_percentage() == 0.0
        
        tracker.update(5)
        assert tracker.get_percentage() == 50.0
        
        tracker.update(10)
        assert tracker.get_percentage() == 100.0
    
    def test_to_dict(self):
        """测试转换为字典"""
        tracker = ProgressTracker("task1", 10, "测试任务")
        tracker.start()
        tracker.update(5, "处理中")
        
        data = tracker.to_dict()
        
        assert data["task_id"] == "task1"
        assert data["description"] == "测试任务"
        assert data["status"] == "in_progress"
        assert data["current_step"] == 5
        assert data["total_steps"] == 10
        assert data["percentage"] == 50.0
        assert data["current_step_description"] == "处理中"


class MockWebSocket:
    """模拟WebSocket连接"""
    
    def __init__(self):
        self.messages = []
        self.accepted = False
        self.closed = False
    
    async def accept(self):
        """接受连接"""
        self.accepted = True
    
    async def send_json(self, data):
        """发送JSON消息"""
        self.messages.append(data)
    
    async def send_text(self, text):
        """发送文本消息"""
        self.messages.append(text)
    
    async def receive_text(self):
        """接收文本消息"""
        await asyncio.sleep(0.1)
        return "ping"


class TestConnectionManager:
    """连接管理器测试"""
    
    @pytest.mark.asyncio
    async def test_connect_websocket(self):
        """测试连接WebSocket"""
        manager = ConnectionManager()
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        
        assert ws.accepted
        assert "user1" in manager.active_connections
        assert ws in manager.active_connections["user1"]
    
    def test_disconnect_websocket(self):
        """测试断开WebSocket连接"""
        manager = ConnectionManager()
        ws = MockWebSocket()
        
        manager.active_connections["user1"] = {ws}
        manager.disconnect(ws, "user1")
        
        assert "user1" not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self):
        """测试发送个人消息"""
        manager = ConnectionManager()
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        await manager.send_personal_message({"type": "test", "message": "hello"}, "user1")
        
        assert len(ws.messages) == 1
        assert ws.messages[0]["type"] == "test"
        assert ws.messages[0]["message"] == "hello"
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self):
        """测试广播消息"""
        manager = ConnectionManager()
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        
        await manager.connect(ws1, "user1")
        await manager.connect(ws2, "user2")
        
        await manager.broadcast({"type": "broadcast", "message": "hello all"})
        
        assert len(ws1.messages) == 1
        assert len(ws2.messages) == 1
    
    def test_create_progress_tracker(self):
        """测试创建进度跟踪器"""
        manager = ConnectionManager()
        
        tracker = manager.create_progress_tracker("task1", 10, "测试任务")
        
        assert tracker.task_id == "task1"
        assert "task1" in manager.progress_trackers
    
    def test_get_progress_tracker(self):
        """测试获取进度跟踪器"""
        manager = ConnectionManager()
        
        tracker = manager.create_progress_tracker("task1", 10)
        retrieved = manager.get_progress_tracker("task1")
        
        assert retrieved == tracker
    
    @pytest.mark.asyncio
    async def test_send_progress_update(self):
        """测试发送进度更新"""
        manager = ConnectionManager()
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        tracker = manager.create_progress_tracker("task1", 10)
        tracker.start()
        tracker.update(5)
        
        await manager.send_progress_update("task1", "user1")
        
        assert len(ws.messages) == 1
        assert ws.messages[0]["type"] == MessageType.PROGRESS.value
        assert ws.messages[0]["data"]["current_step"] == 5
    
    @pytest.mark.asyncio
    async def test_send_status_message(self):
        """测试发送状态消息"""
        manager = ConnectionManager()
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        await manager.send_status_message("user1", "processing", "正在处理")
        
        assert len(ws.messages) == 1
        assert ws.messages[0]["type"] == MessageType.STATUS.value
        assert ws.messages[0]["status"] == "processing"
    
    @pytest.mark.asyncio
    async def test_send_error_message(self):
        """测试发送错误消息"""
        manager = ConnectionManager()
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        await manager.send_error_message("user1", "错误", "详细信息")
        
        assert len(ws.messages) == 1
        assert ws.messages[0]["type"] == MessageType.ERROR.value
        assert ws.messages[0]["error"] == "错误"
    
    @pytest.mark.asyncio
    async def test_send_success_message(self):
        """测试发送成功消息"""
        manager = ConnectionManager()
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        await manager.send_success_message("user1", "成功", {"result": "ok"})
        
        assert len(ws.messages) == 1
        assert ws.messages[0]["type"] == MessageType.SUCCESS.value
        assert ws.messages[0]["message"] == "成功"
    
    def test_cleanup_old_trackers(self):
        """测试清理旧的跟踪器"""
        manager = ConnectionManager()
        
        # 创建一个已完成的跟踪器
        tracker = manager.create_progress_tracker("task1", 10)
        tracker.start()
        tracker.complete()
        
        # 修改完成时间为25小时前
        from datetime import timedelta
        tracker.completed_at = datetime.utcnow() - timedelta(hours=25)
        
        manager.cleanup_old_trackers(max_age_hours=24)
        
        assert "task1" not in manager.progress_trackers


class TestRealtimeFeedbackService:
    """实时反馈服务测试"""
    
    @pytest.mark.asyncio
    async def test_start_task(self):
        """测试开始任务"""
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        tracker = await service.start_task("task1", "user1", 10, "测试任务")
        
        assert tracker.status == ProgressStatus.IN_PROGRESS
        assert len(ws.messages) == 2  # 状态消息 + 进度更新
    
    @pytest.mark.asyncio
    async def test_update_progress(self):
        """测试更新进度"""
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        await service.start_task("task1", "user1", 10)
        
        ws.messages.clear()
        await service.update_progress("task1", "user1", 5, "处理中")
        
        assert len(ws.messages) == 1
        assert ws.messages[0]["data"]["current_step"] == 5
    
    @pytest.mark.asyncio
    async def test_complete_task(self):
        """测试完成任务"""
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        await service.start_task("task1", "user1", 10)
        
        ws.messages.clear()
        await service.complete_task("task1", "user1", {"result": "success"})
        
        assert len(ws.messages) == 2  # 进度更新 + 成功消息
        tracker = manager.get_progress_tracker("task1")
        assert tracker.status == ProgressStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_fail_task(self):
        """测试任务失败"""
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        await service.start_task("task1", "user1", 10)
        
        ws.messages.clear()
        await service.fail_task("task1", "user1", "错误信息")
        
        assert len(ws.messages) == 2  # 进度更新 + 错误消息
        tracker = manager.get_progress_tracker("task1")
        assert tracker.status == ProgressStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_cancel_task(self):
        """测试取消任务"""
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        await service.start_task("task1", "user1", 10)
        
        ws.messages.clear()
        await service.cancel_task("task1", "user1")
        
        assert len(ws.messages) == 2  # 进度更新 + 信息消息
        tracker = manager.get_progress_tracker("task1")
        assert tracker.status == ProgressStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_send_notification(self):
        """测试发送通知"""
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, "user1")
        
        await service.send_notification("user1", "测试通知", "info")
        assert len(ws.messages) == 1
        
        await service.send_notification("user1", "成功通知", "success")
        assert len(ws.messages) == 2
        
        await service.send_notification("user1", "错误通知", "error")
        assert len(ws.messages) == 3
