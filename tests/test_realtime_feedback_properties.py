"""实时反馈属性测试

属性47：实时反馈
对于任意主要操作，系统应提供实时反馈和进度指示

验证需求：13.3
"""
import pytest
import asyncio
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime

from app.services.realtime_feedback import (
    ProgressTracker,
    ProgressStatus,
    ConnectionManager,
    RealtimeFeedbackService,
    MessageType
)


# Hypothesis策略
task_ids = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters='\x00'))
descriptions = st.text(min_size=0, max_size=200)
step_numbers = st.integers(min_value=0, max_value=1000)
total_steps = st.integers(min_value=1, max_value=1000)
user_ids = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters='\x00'))


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


class TestRealtimeFeedbackProperties:
    """实时反馈属性测试"""
    
    @given(
        task_id=task_ids,
        total=total_steps,
        description=descriptions
    )
    @settings(max_examples=100, deadline=None)
    def test_property_progress_tracker_percentage_is_valid(
        self,
        task_id: str,
        total: int,
        description: str
    ):
        """
        属性：进度百分比始终在0-100之间
        
        对于任意的任务和步骤数，计算的百分比应该在有效范围内
        """
        tracker = ProgressTracker(task_id, total, description)
        
        # 初始百分比应该是0
        assert 0 <= tracker.get_percentage() <= 100
        
        # 更新到任意步骤
        for step in range(0, total + 1):
            tracker.update(step)
            percentage = tracker.get_percentage()
            assert 0 <= percentage <= 100
            
            # 验证百分比计算正确
            expected = (step / total * 100) if total > 0 else 0
            assert abs(percentage - expected) < 0.01
    
    @given(
        task_id=task_ids,
        total=total_steps,
        current=step_numbers
    )
    @settings(max_examples=100, deadline=None)
    def test_property_progress_tracker_state_transitions_are_valid(
        self,
        task_id: str,
        total: int,
        current: int
    ):
        """
        属性：进度跟踪器的状态转换是有效的
        
        对于任意的任务，状态转换应该遵循预定义的规则
        """
        assume(0 <= current <= total)
        
        tracker = ProgressTracker(task_id, total)
        
        # 初始状态应该是PENDING
        assert tracker.status == ProgressStatus.PENDING
        
        # 开始后状态应该是IN_PROGRESS
        tracker.start()
        assert tracker.status == ProgressStatus.IN_PROGRESS
        assert tracker.started_at is not None
        
        # 更新进度不应该改变状态
        tracker.update(current)
        assert tracker.status == ProgressStatus.IN_PROGRESS
        
        # 完成后状态应该是COMPLETED
        tracker.complete()
        assert tracker.status == ProgressStatus.COMPLETED
        assert tracker.completed_at is not None
    
    @given(
        task_id=task_ids,
        total=total_steps
    )
    @settings(max_examples=100, deadline=None)
    def test_property_progress_tracker_to_dict_contains_required_fields(
        self,
        task_id: str,
        total: int
    ):
        """
        属性：进度跟踪器转换为字典包含所有必需字段
        
        对于任意的任务，转换后的字典应该包含所有必需的字段
        """
        tracker = ProgressTracker(task_id, total)
        tracker.start()
        
        data = tracker.to_dict()
        
        # 验证必需字段存在
        required_fields = [
            "task_id",
            "description",
            "status",
            "current_step",
            "total_steps",
            "percentage",
            "started_at",
            "completed_at",
            "error_message",
            "current_step_description"
        ]
        
        for field in required_fields:
            assert field in data
        
        # 验证字段类型
        assert isinstance(data["task_id"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["current_step"], int)
        assert isinstance(data["total_steps"], int)
        assert isinstance(data["percentage"], (int, float))
    
    @pytest.mark.asyncio
    @given(
        user_id=user_ids,
        task_id=task_ids,
        total=total_steps
    )
    @settings(max_examples=50, deadline=None)
    async def test_property_realtime_feedback_provides_progress_updates(
        self,
        user_id: str,
        task_id: str,
        total: int
    ):
        """
        属性47：实时反馈
        
        对于任意主要操作，系统应提供实时反馈和进度指示
        
        验证：
        1. 任务开始时发送通知
        2. 进度更新时发送消息
        3. 任务完成时发送通知
        """
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        # 连接WebSocket
        await manager.connect(ws, user_id)
        
        # 开始任务
        tracker = await service.start_task(task_id, user_id, total, "测试任务")
        
        # 验证：任务开始时应该发送消息
        assert len(ws.messages) >= 2  # 至少有状态消息和进度更新
        
        # 验证：消息包含正确的类型
        message_types = [msg.get("type") for msg in ws.messages if isinstance(msg, dict)]
        assert MessageType.STATUS.value in message_types or MessageType.PROGRESS.value in message_types
        
        # 清空消息
        ws.messages.clear()
        
        # 更新进度
        mid_step = total // 2 if total > 1 else 1
        await service.update_progress(task_id, user_id, mid_step, "处理中")
        
        # 验证：进度更新时应该发送消息
        assert len(ws.messages) >= 1
        progress_msg = next((msg for msg in ws.messages if isinstance(msg, dict) and msg.get("type") == MessageType.PROGRESS.value), None)
        assert progress_msg is not None
        assert "data" in progress_msg
        
        # 清空消息
        ws.messages.clear()
        
        # 完成任务
        await service.complete_task(task_id, user_id, {"result": "success"})
        
        # 验证：任务完成时应该发送消息
        assert len(ws.messages) >= 2  # 进度更新 + 成功消息
        success_msg = next((msg for msg in ws.messages if isinstance(msg, dict) and msg.get("type") == MessageType.SUCCESS.value), None)
        assert success_msg is not None
    
    @pytest.mark.asyncio
    @given(
        user_id=user_ids,
        task_id=task_ids,
        total=total_steps,
        error_msg=descriptions
    )
    @settings(max_examples=50, deadline=None)
    async def test_property_realtime_feedback_handles_task_failure(
        self,
        user_id: str,
        task_id: str,
        total: int,
        error_msg: str
    ):
        """
        属性：实时反馈处理任务失败
        
        对于任意失败的操作，系统应该提供错误反馈
        """
        assume(len(error_msg) > 0)  # 错误消息不能为空
        
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, user_id)
        
        # 开始任务
        await service.start_task(task_id, user_id, total)
        ws.messages.clear()
        
        # 任务失败
        await service.fail_task(task_id, user_id, error_msg)
        
        # 验证：失败时应该发送错误消息
        assert len(ws.messages) >= 1
        error_msg_found = next((msg for msg in ws.messages if isinstance(msg, dict) and msg.get("type") == MessageType.ERROR.value), None)
        assert error_msg_found is not None
        
        # 验证：跟踪器状态应该是FAILED
        tracker = manager.get_progress_tracker(task_id)
        assert tracker.status == ProgressStatus.FAILED
        assert tracker.error_message == error_msg
    
    @pytest.mark.asyncio
    @given(
        user_id=user_ids,
        message=descriptions
    )
    @settings(max_examples=50, deadline=None)
    async def test_property_realtime_feedback_delivers_notifications(
        self,
        user_id: str,
        message: str
    ):
        """
        属性：实时反馈传递通知
        
        对于任意通知，系统应该成功传递给用户
        """
        assume(len(message) > 0)
        
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, user_id)
        
        # 发送不同类型的通知
        notification_types = ["info", "success", "error"]
        
        for notif_type in notification_types:
            ws.messages.clear()
            await service.send_notification(user_id, message, notif_type)
            
            # 验证：通知应该被传递
            assert len(ws.messages) >= 1
            
            # 验证：消息包含正确的内容
            msg = ws.messages[0]
            assert isinstance(msg, dict)
            assert "type" in msg
            assert "timestamp" in msg
    
    @given(
        task_id=task_ids,
        total=total_steps,
        steps=st.lists(step_numbers, min_size=1, max_size=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_progress_is_monotonic(
        self,
        task_id: str,
        total: int,
        steps: list
    ):
        """
        属性：进度是单调递增的
        
        对于任意的步骤序列，进度百分比应该单调递增（或保持不变）
        """
        # 过滤并排序步骤
        valid_steps = [s for s in steps if 0 <= s <= total]
        assume(len(valid_steps) > 0)
        valid_steps = sorted(set(valid_steps))
        
        tracker = ProgressTracker(task_id, total)
        tracker.start()
        
        previous_percentage = 0
        
        for step in valid_steps:
            tracker.update(step)
            current_percentage = tracker.get_percentage()
            
            # 验证：进度应该单调递增
            assert current_percentage >= previous_percentage
            previous_percentage = current_percentage
    
    @pytest.mark.asyncio
    @given(
        user_ids_list=st.lists(user_ids, min_size=2, max_size=5, unique=True),
        task_id=task_ids,
        total=total_steps
    )
    @settings(max_examples=30, deadline=None)
    async def test_property_messages_are_isolated_per_user(
        self,
        user_ids_list: list,
        task_id: str,
        total: int
    ):
        """
        属性：消息按用户隔离
        
        对于多个用户，每个用户应该只收到发送给他们的消息
        """
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        
        # 为每个用户创建WebSocket连接
        websockets = {}
        for uid in user_ids_list:
            ws = MockWebSocket()
            await manager.connect(ws, uid)
            websockets[uid] = ws
        
        # 为第一个用户发送消息
        target_user = user_ids_list[0]
        await service.send_notification(target_user, "测试消息", "info")
        
        # 验证：只有目标用户收到消息
        assert len(websockets[target_user].messages) >= 1
        
        # 验证：其他用户没有收到消息
        for uid in user_ids_list[1:]:
            assert len(websockets[uid].messages) == 0
    
    @given(
        task_id=task_ids,
        total=total_steps
    )
    @settings(max_examples=100, deadline=None)
    def test_property_completed_task_has_100_percent(
        self,
        task_id: str,
        total: int
    ):
        """
        属性：完成的任务进度为100%
        
        对于任意完成的任务，进度应该是100%
        """
        tracker = ProgressTracker(task_id, total)
        tracker.start()
        tracker.complete()
        
        # 验证：完成的任务进度应该是100%
        assert tracker.get_percentage() == 100.0
        assert tracker.current_step == total
        assert tracker.status == ProgressStatus.COMPLETED
    
    @pytest.mark.asyncio
    @given(
        user_id=user_ids,
        task_id=task_ids,
        total=total_steps
    )
    @settings(max_examples=50, deadline=None)
    async def test_property_progress_updates_are_timely(
        self,
        user_id: str,
        task_id: str,
        total: int
    ):
        """
        属性：进度更新是及时的
        
        对于任意的进度更新，消息应该立即发送（不延迟）
        """
        manager = ConnectionManager()
        service = RealtimeFeedbackService(manager)
        ws = MockWebSocket()
        
        await manager.connect(ws, user_id)
        
        # 记录开始时间
        start_time = datetime.utcnow()
        
        # 开始任务
        await service.start_task(task_id, user_id, total)
        
        # 记录结束时间
        end_time = datetime.utcnow()
        
        # 验证：消息应该在合理时间内发送（< 1秒）
        elapsed = (end_time - start_time).total_seconds()
        assert elapsed < 1.0
        
        # 验证：消息已经发送
        assert len(ws.messages) >= 1
