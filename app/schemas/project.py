"""项目相关的Pydantic模式"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.project import AspectRatio


class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")
    aspect_ratio: AspectRatio = Field(default=AspectRatio.VERTICAL_9_16, description="画面比例")
    duration_minutes: Optional[float] = Field(None, ge=0, le=180, description="目标时长（分钟）")
    script: Optional[str] = Field(None, description="剧本内容")


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="项目名称")
    aspect_ratio: Optional[AspectRatio] = Field(None, description="画面比例")
    duration_minutes: Optional[float] = Field(None, ge=0, le=180, description="目标时长（分钟）")
    script: Optional[str] = Field(None, description="剧本内容")


class ProjectResponse(BaseModel):
    """项目响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    name: str
    aspect_ratio: AspectRatio
    duration_minutes: Optional[float]
    script: Optional[str]
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    projects: list[ProjectResponse]
    total: int
    page: int
    page_size: int
