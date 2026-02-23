"""分镜服务层"""
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from typing import List, Optional
from uuid import UUID

from app.models.storyboard import StoryboardFrame
from app.schemas.storyboard import StoryboardFrameCreate, StoryboardFrameUpdate


class StoryboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_frames(self, project_id: UUID) -> List[StoryboardFrame]:
        """获取项目的所有分镜帧"""
        stmt = select(StoryboardFrame).where(
            StoryboardFrame.project_id == project_id
        ).order_by(StoryboardFrame.sequence_number)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_frame(self, frame_id: UUID) -> Optional[StoryboardFrame]:
        """获取单个分镜帧"""
        return self.db.get(StoryboardFrame, frame_id)

    def create_frame(self, data: StoryboardFrameCreate) -> StoryboardFrame:
        """创建分镜帧"""
        # 获取当前最大序号
        stmt = select(func.max(StoryboardFrame.sequence_number)).where(
            StoryboardFrame.project_id == data.project_id
        )
        max_seq = self.db.execute(stmt).scalar() or 0
        
        # Convert Pydantic model to DB model
        # Note: We mapped `scene_description` to `description` in the model
        # and `character_id` to `character_ids` array
        
        frame = StoryboardFrame(
            project_id=data.project_id,
            sequence_number=max_seq + 1,
            description=data.scene_description, # Map scene_description to description
            character_ids=[data.character_id] if data.character_id else [], # Map single ID to array
            status="pending"
        )
        
        self.db.add(frame)
        self.db.commit()
        self.db.refresh(frame)
        return frame

    def update_frame(self, frame_id: UUID, data: StoryboardFrameUpdate) -> Optional[StoryboardFrame]:
        """更新分镜帧"""
        frame = self.get_frame(frame_id)
        if not frame:
            return None
            
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(frame, field, value)
            
        self.db.add(frame)
        self.db.commit()
        self.db.refresh(frame)
        return frame

    def delete_frame(self, frame_id: UUID) -> bool:
        """删除分镜帧"""
        frame = self.get_frame(frame_id)
        if not frame:
            return False
            
        self.db.delete(frame)
        self.db.commit()
        return True
