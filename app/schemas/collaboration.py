"""协作相关的Pydantic模式"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.collaboration import CollaboratorRole, InvitationStatus


class InvitationCreate(BaseModel):
    """创建邀请请求"""
    email: EmailStr = Field(..., description="被邀请者邮箱")
    role: CollaboratorRole = Field(default=CollaboratorRole.VIEWER, description="协作者角色")


class InvitationResponse(BaseModel):
    """邀请响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    inviter_id: UUID
    invitee_email: str
    role: CollaboratorRole
    status: InvitationStatus
    created_at: datetime
    updated_at: datetime


class InvitationAccept(BaseModel):
    """接受邀请请求"""
    invitation_id: UUID = Field(..., description="邀请ID")


class CollaboratorResponse(BaseModel):
    """协作者响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    user_id: UUID
    role: CollaboratorRole
    created_at: datetime


class CollaboratorUpdate(BaseModel):
    """更新协作者请求"""
    role: CollaboratorRole = Field(..., description="新的角色")


class VersionCreate(BaseModel):
    """创建版本请求"""
    description: Optional[str] = Field(None, max_length=500, description="版本描述")


class VersionResponse(BaseModel):
    """版本响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    version_number: int
    description: Optional[str]
    created_by: UUID
    created_at: datetime


class TemplateCreate(BaseModel):
    """创建模板请求"""
    name: str = Field(..., min_length=1, max_length=255, description="模板名称")
    description: Optional[str] = Field(None, max_length=1000, description="模板描述")
    is_public: bool = Field(default=False, description="是否公开")


class TemplateResponse(BaseModel):
    """模板响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: Optional[str]
    created_by: UUID
    is_public: str
    created_at: datetime
