"""分镜管理API端点"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.storyboard import StoryboardService
from app.schemas.storyboard import (
    StoryboardFrameCreate,
    StoryboardFrameUpdate,
    StoryboardFrameResponse
)

router = APIRouter(prefix="/storyboards", tags=["storyboards"])

@router.post("", response_model=StoryboardFrameResponse, status_code=status.HTTP_201_CREATED)
def create_storyboard_frame(
    frame_data: StoryboardFrameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新分镜帧
    """
    # TODO: Verify project ownership if needed
    service = StoryboardService(db)
    return service.create_frame(frame_data)

@router.get("", response_model=List[StoryboardFrameResponse])
def list_storyboard_frames(
    project_id: UUID = Query(..., description="项目ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取项目的所有分镜帧
    """
    service = StoryboardService(db)
    return service.get_frames(project_id)

@router.get("/{frame_id}", response_model=StoryboardFrameResponse)
def get_storyboard_frame(
    frame_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个分镜帧详情
    """
    service = StoryboardService(db)
    frame = service.get_frame(frame_id)
    if not frame:
        raise HTTPException(status_code=404, detail="分镜不存在")
    return frame

@router.put("/{frame_id}", response_model=StoryboardFrameResponse)
def update_storyboard_frame(
    frame_id: UUID,
    frame_data: StoryboardFrameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新分镜帧
    """
    service = StoryboardService(db)
    updated_frame = service.update_frame(frame_id, frame_data)
    if not updated_frame:
        raise HTTPException(status_code=404, detail="分镜不存在")
    return updated_frame

@router.delete("/{frame_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_storyboard_frame(
    frame_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除分镜帧
    """
    service = StoryboardService(db)
    success = service.delete_frame(frame_id)
    if not success:
        raise HTTPException(status_code=404, detail="分镜不存在")
