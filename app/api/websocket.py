"""WebSocket API端点"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional

from app.services.realtime_feedback import connection_manager, realtime_feedback_service
from app.api.dependencies import get_current_user_ws
from app.models.user import User


router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/feedback")
async def websocket_feedback_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket端点用于实时反馈
    
    客户端需要在查询参数中提供token进行认证
    """
    # 简化的认证逻辑（实际应该验证token）
    # 这里假设token就是user_id（实际应该解析JWT）
    user_id = token if token else "anonymous"
    
    await connection_manager.connect(websocket, user_id)
    
    try:
        # 发送欢迎消息
        await connection_manager.send_info_message(
            user_id,
            "WebSocket连接已建立",
            {"user_id": user_id}
        )
        
        # 保持连接并接收消息
        while True:
            data = await websocket.receive_text()
            
            # 处理客户端消息（例如心跳、订阅特定任务等）
            if data == "ping":
                await websocket.send_text("pong")
            elif data.startswith("subscribe:"):
                task_id = data.split(":", 1)[1]
                # 发送任务的当前进度
                await connection_manager.send_progress_update(task_id, user_id)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id)
    except Exception as e:
        connection_manager.disconnect(websocket, user_id)
        raise


@router.websocket("/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket端点用于通知推送
    
    客户端需要在查询参数中提供token进行认证
    """
    user_id = token if token else "anonymous"
    
    await connection_manager.connect(websocket, user_id)
    
    try:
        await connection_manager.send_info_message(
            user_id,
            "通知服务已连接",
            {"user_id": user_id}
        )
        
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id)
    except Exception as e:
        connection_manager.disconnect(websocket, user_id)
        raise
