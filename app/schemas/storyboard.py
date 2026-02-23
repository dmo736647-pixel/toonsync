"""分镜相关的Pydantic模式"""
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

class StoryboardFrameCreate(BaseModel):
    """创建分镜帧请求"""
    project_id: UUID = Field(..., description="项目ID")
    scene_description: str = Field(..., description="场景描述")
    character_id: Optional[UUID] = Field(None, description="角色ID")
    style: Optional[str] = Field("anime", description="风格")

class StoryboardFrameUpdate(BaseModel):
    """更新分镜帧请求"""
    scene_description: Optional[str] = Field(None, description="场景描述")
    sequence_number: Optional[int] = Field(None, description="序号")
    image_url: Optional[str] = Field(None, description="图片URL")

class StoryboardFrameResponse(BaseModel):
    """分镜帧响应"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: UUID
    project_id: UUID
    sequence_number: int
    scene_description: Optional[str] = Field(None, alias="description")
    
    # We define character_ids as list, and frontend can use first one
    character_ids: Optional[List[UUID]] = None
    
    # character_id is now a property below, remove field definition
    # character_id: Optional[UUID] = None

    @model_validator(mode='before')
    @classmethod
    def populate_character_id_from_orm(cls, data: Any) -> Any:
        return data

    @property
    def character_id(self) -> Optional[UUID]:
        if self.character_ids and len(self.character_ids) > 0:
            return self.character_ids[0]
        return None

    
    image_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None 


class StoryboardListResponse(BaseModel):
    """分镜列表响应"""
    frames: List[StoryboardFrameResponse]
