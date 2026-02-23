"""协作管理API端点"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.collaboration import CollaborationService, VersionService, TemplateService
from app.schemas.collaboration import (
    InvitationCreate,
    InvitationResponse,
    InvitationAccept,
    CollaboratorResponse,
    CollaboratorUpdate,
    VersionCreate,
    VersionResponse,
    TemplateCreate,
    TemplateResponse,
)


router = APIRouter(prefix="/collaboration", tags=["collaboration"])


@router.post("/projects/{project_id}/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def invite_collaborator(
    project_id: UUID,
    invitation_data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    邀请团队成员
    
    - **email**: 被邀请者邮箱
    - **role**: 协作者角色（viewer/editor/admin）
    """
    service = CollaborationService(db)
    invitation = await service.invite_collaborator(project_id, current_user.id, invitation_data)
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限邀请协作者或邀请已存在"
        )
    
    return invitation


@router.post("/invitations/accept", response_model=CollaboratorResponse)
async def accept_invitation(
    accept_data: InvitationAccept,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    接受邀请
    
    - **invitation_id**: 邀请ID
    """
    service = CollaborationService(db)
    collaborator = await service.accept_invitation(accept_data.invitation_id, current_user.id)
    
    if not collaborator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请不存在、已过期或邮箱不匹配"
        )
    
    return collaborator


@router.get("/projects/{project_id}/collaborators", response_model=List[CollaboratorResponse])
async def list_collaborators(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    列出项目协作者
    """
    service = CollaborationService(db)
    collaborators = await service.list_collaborators(project_id, current_user.id)
    
    if collaborators is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看协作者列表"
        )
    
    return collaborators


@router.put("/collaborators/{collaborator_id}", response_model=CollaboratorResponse)
async def update_collaborator_role(
    collaborator_id: UUID,
    update_data: CollaboratorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新协作者角色
    
    - **role**: 新的角色（viewer/editor/admin）
    """
    service = CollaborationService(db)
    collaborator = await service.update_collaborator_role(collaborator_id, current_user.id, update_data)
    
    if not collaborator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限更新协作者角色"
        )
    
    return collaborator


@router.delete("/collaborators/{collaborator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_collaborator(
    collaborator_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    移除协作者
    """
    service = CollaborationService(db)
    success = await service.remove_collaborator(collaborator_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限移除协作者"
        )


@router.post("/projects/{project_id}/versions", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    project_id: UUID,
    version_data: VersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建项目版本
    
    - **description**: 版本描述（可选）
    """
    service = VersionService(db)
    version = await service.create_version(project_id, current_user.id, version_data)
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return version


@router.get("/projects/{project_id}/versions", response_model=List[VersionResponse])
async def list_versions(
    project_id: UUID,
    days: int = Query(30, ge=1, le=90, description="保留天数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    列出项目版本历史
    
    默认显示最近30天的版本
    """
    service = VersionService(db)
    versions = await service.list_versions(project_id, current_user.id, days)
    
    if versions is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看版本历史"
        )
    
    return versions


@router.post("/projects/{project_id}/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    project_id: UUID,
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    从项目创建模板
    
    - **name**: 模板名称
    - **description**: 模板描述（可选）
    - **is_public**: 是否公开（默认false）
    """
    service = TemplateService(db)
    template = await service.create_template(project_id, current_user.id, template_data)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在或无权限"
        )
    
    return template


@router.post("/templates/{template_id}/apply/{project_id}", status_code=status.HTTP_200_OK)
async def apply_template(
    template_id: UUID,
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    应用模板到项目
    """
    service = TemplateService(db)
    project = await service.apply_template(template_id, project_id, current_user.id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板或项目不存在"
        )
    
    return {"message": "模板应用成功", "project_id": str(project.id)}
