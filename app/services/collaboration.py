"""协作管理服务"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import json

from app.models.collaboration import (
    ProjectCollaborator,
    ProjectInvitation,
    ProjectVersion,
    ProjectTemplate,
    CollaboratorRole,
    InvitationStatus,
)
from app.models.project import Project
from app.models.user import User
from app.schemas.collaboration import (
    InvitationCreate,
    CollaboratorUpdate,
    VersionCreate,
    TemplateCreate,
)


class CollaborationService:
    """协作管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def invite_collaborator(
        self,
        project_id: UUID,
        inviter_id: UUID,
        invitation_data: InvitationCreate
    ) -> Optional[ProjectInvitation]:
        """
        邀请团队成员
        
        参数:
            project_id: 项目ID
            inviter_id: 邀请者ID
            invitation_data: 邀请数据
        
        返回:
            Optional[ProjectInvitation]: 邀请对象，如果项目不存在或无权限则返回None
        """
        # 验证邀请者是否有权限（必须是项目所有者或管理员）
        has_permission = await self._check_admin_permission(project_id, inviter_id)
        if not has_permission:
            return None
        
        # 检查是否已经邀请过
        existing_invitation = await self.db.execute(
            select(ProjectInvitation).where(
                and_(
                    ProjectInvitation.project_id == project_id,
                    ProjectInvitation.invitee_email == invitation_data.email,
                    ProjectInvitation.status == InvitationStatus.PENDING
                )
            )
        )
        if existing_invitation.scalar_one_or_none():
            return None  # 已有待处理的邀请
        
        # 创建邀请
        invitation = ProjectInvitation(
            project_id=project_id,
            inviter_id=inviter_id,
            invitee_email=invitation_data.email,
            role=invitation_data.role,
            status=InvitationStatus.PENDING
        )
        
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        
        return invitation
    
    async def accept_invitation(
        self,
        invitation_id: UUID,
        user_id: UUID
    ) -> Optional[ProjectCollaborator]:
        """
        接受邀请
        
        参数:
            invitation_id: 邀请ID
            user_id: 用户ID
        
        返回:
            Optional[ProjectCollaborator]: 协作者对象，如果邀请不存在或无效则返回None
        """
        # 获取邀请
        result = await self.db.execute(
            select(ProjectInvitation)
            .where(ProjectInvitation.id == invitation_id)
            .options(selectinload(ProjectInvitation.project))
        )
        invitation = result.scalar_one_or_none()
        
        if not invitation or invitation.status != InvitationStatus.PENDING:
            return None
        
        # 验证用户邮箱匹配
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user or user.email != invitation.invitee_email:
            return None
        
        # 检查是否已经是协作者
        existing_collab = await self.db.execute(
            select(ProjectCollaborator).where(
                and_(
                    ProjectCollaborator.project_id == invitation.project_id,
                    ProjectCollaborator.user_id == user_id
                )
            )
        )
        if existing_collab.scalar_one_or_none():
            return None
        
        # 创建协作者
        collaborator = ProjectCollaborator(
            project_id=invitation.project_id,
            user_id=user_id,
            role=invitation.role
        )
        
        # 更新邀请状态
        invitation.status = InvitationStatus.ACCEPTED
        
        self.db.add(collaborator)
        await self.db.commit()
        await self.db.refresh(collaborator)
        
        return collaborator
    
    async def list_collaborators(
        self,
        project_id: UUID,
        user_id: UUID
    ) -> Optional[List[ProjectCollaborator]]:
        """
        列出项目协作者
        
        参数:
            project_id: 项目ID
            user_id: 用户ID（用于权限验证）
        
        返回:
            Optional[List[ProjectCollaborator]]: 协作者列表，如果无权限则返回None
        """
        # 验证用户是否有权限查看
        has_permission = await self._check_project_access(project_id, user_id)
        if not has_permission:
            return None
        
        result = await self.db.execute(
            select(ProjectCollaborator)
            .where(ProjectCollaborator.project_id == project_id)
            .options(selectinload(ProjectCollaborator.user))
        )
        
        return list(result.scalars().all())
    
    async def update_collaborator_role(
        self,
        collaborator_id: UUID,
        user_id: UUID,
        update_data: CollaboratorUpdate
    ) -> Optional[ProjectCollaborator]:
        """
        更新协作者角色
        
        参数:
            collaborator_id: 协作者ID
            user_id: 操作用户ID（必须是管理员）
            update_data: 更新数据
        
        返回:
            Optional[ProjectCollaborator]: 更新后的协作者对象
        """
        # 获取协作者
        result = await self.db.execute(
            select(ProjectCollaborator).where(ProjectCollaborator.id == collaborator_id)
        )
        collaborator = result.scalar_one_or_none()
        
        if not collaborator:
            return None
        
        # 验证操作用户是否有权限
        has_permission = await self._check_admin_permission(collaborator.project_id, user_id)
        if not has_permission:
            return None
        
        # 更新角色
        collaborator.role = update_data.role
        
        await self.db.commit()
        await self.db.refresh(collaborator)
        
        return collaborator
    
    async def remove_collaborator(
        self,
        collaborator_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        移除协作者
        
        参数:
            collaborator_id: 协作者ID
            user_id: 操作用户ID（必须是管理员）
        
        返回:
            bool: 是否移除成功
        """
        # 获取协作者
        result = await self.db.execute(
            select(ProjectCollaborator).where(ProjectCollaborator.id == collaborator_id)
        )
        collaborator = result.scalar_one_or_none()
        
        if not collaborator:
            return False
        
        # 验证操作用户是否有权限
        has_permission = await self._check_admin_permission(collaborator.project_id, user_id)
        if not has_permission:
            return False
        
        await self.db.delete(collaborator)
        await self.db.commit()
        
        return True
    
    async def check_edit_conflict(
        self,
        project_id: UUID,
        user_id: UUID,
        last_known_version: datetime
    ) -> bool:
        """
        检查并发编辑冲突（乐观锁）
        
        参数:
            project_id: 项目ID
            user_id: 用户ID
            last_known_version: 用户最后已知的版本时间戳
        
        返回:
            bool: 是否存在冲突（True表示有冲突）
        """
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return True
        
        # 如果项目的更新时间晚于用户最后已知的版本，说明有冲突
        return project.updated_at > last_known_version
    
    async def _check_project_access(self, project_id: UUID, user_id: UUID) -> bool:
        """检查用户是否有项目访问权限"""
        # 检查是否是项目所有者
        result = await self.db.execute(
            select(Project).where(
                and_(Project.id == project_id, Project.user_id == user_id)
            )
        )
        if result.scalar_one_or_none():
            return True
        
        # 检查是否是协作者
        result = await self.db.execute(
            select(ProjectCollaborator).where(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def _check_admin_permission(self, project_id: UUID, user_id: UUID) -> bool:
        """检查用户是否有管理员权限"""
        # 检查是否是项目所有者
        result = await self.db.execute(
            select(Project).where(
                and_(Project.id == project_id, Project.user_id == user_id)
            )
        )
        if result.scalar_one_or_none():
            return True
        
        # 检查是否是管理员协作者
        result = await self.db.execute(
            select(ProjectCollaborator).where(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == user_id,
                    ProjectCollaborator.role == CollaboratorRole.ADMIN
                )
            )
        )
        return result.scalar_one_or_none() is not None


class VersionService:
    """版本管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_version(
        self,
        project_id: UUID,
        user_id: UUID,
        version_data: VersionCreate
    ) -> Optional[ProjectVersion]:
        """
        创建项目版本
        
        参数:
            project_id: 项目ID
            user_id: 用户ID
            version_data: 版本数据
        
        返回:
            Optional[ProjectVersion]: 版本对象
        """
        # 获取项目
        result = await self.db.execute(
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.characters),
                selectinload(Project.storyboard_frames),
                selectinload(Project.audio_tracks)
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return None
        
        # 获取当前版本号
        count_result = await self.db.execute(
            select(func.count(ProjectVersion.id)).where(
                ProjectVersion.project_id == project_id
            )
        )
        version_number = count_result.scalar_one() + 1
        
        # 创建项目快照
        snapshot = {
            "name": project.name,
            "aspect_ratio": project.aspect_ratio.value,
            "duration_minutes": project.duration_minutes,
            "script": project.script,
            "character_count": len(project.characters),
            "frame_count": len(project.storyboard_frames),
            "audio_count": len(project.audio_tracks),
        }
        
        # 创建版本
        version = ProjectVersion(
            project_id=project_id,
            version_number=version_number,
            description=version_data.description,
            snapshot_data=json.dumps(snapshot),
            created_by=user_id
        )
        
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        
        return version
    
    async def list_versions(
        self,
        project_id: UUID,
        user_id: UUID,
        days: int = 30
    ) -> Optional[List[ProjectVersion]]:
        """
        列出项目版本历史
        
        参数:
            project_id: 项目ID
            user_id: 用户ID（用于权限验证）
            days: 保留天数（默认30天）
        
        返回:
            Optional[List[ProjectVersion]]: 版本列表
        """
        # 验证权限
        collab_service = CollaborationService(self.db)
        has_permission = await collab_service._check_project_access(project_id, user_id)
        if not has_permission:
            return None
        
        # 计算截止日期
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(ProjectVersion)
            .where(
                and_(
                    ProjectVersion.project_id == project_id,
                    ProjectVersion.created_at >= cutoff_date
                )
            )
            .order_by(ProjectVersion.version_number.desc())
        )
        
        return list(result.scalars().all())


class TemplateService:
    """模板管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_template(
        self,
        project_id: UUID,
        user_id: UUID,
        template_data: TemplateCreate
    ) -> Optional[ProjectTemplate]:
        """
        从项目创建模板
        
        参数:
            project_id: 项目ID
            user_id: 用户ID
            template_data: 模板数据
        
        返回:
            Optional[ProjectTemplate]: 模板对象
        """
        # 获取项目
        result = await self.db.execute(
            select(Project).where(
                and_(Project.id == project_id, Project.user_id == user_id)
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return None
        
        # 创建模板数据
        template_json = {
            "aspect_ratio": project.aspect_ratio.value,
            "duration_minutes": project.duration_minutes,
            "script_template": project.script,
        }
        
        # 创建模板
        template = ProjectTemplate(
            name=template_data.name,
            description=template_data.description,
            template_data=json.dumps(template_json),
            created_by=user_id,
            is_public='PUBLIC' if template_data.is_public else 'PRIVATE'
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return template
    
    async def apply_template(
        self,
        template_id: UUID,
        project_id: UUID,
        user_id: UUID
    ) -> Optional[Project]:
        """
        应用模板到项目
        
        参数:
            template_id: 模板ID
            project_id: 项目ID
            user_id: 用户ID
        
        返回:
            Optional[Project]: 更新后的项目对象
        """
        # 获取模板
        template_result = await self.db.execute(
            select(ProjectTemplate).where(ProjectTemplate.id == template_id)
        )
        template = template_result.scalar_one_or_none()
        
        if not template:
            return None
        
        # 获取项目
        project_result = await self.db.execute(
            select(Project).where(
                and_(Project.id == project_id, Project.user_id == user_id)
            )
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            return None
        
        # 应用模板
        template_data = json.loads(template.template_data)
        
        if "aspect_ratio" in template_data:
            from app.models.project import AspectRatio
            project.aspect_ratio = AspectRatio(template_data["aspect_ratio"])
        
        if "duration_minutes" in template_data:
            project.duration_minutes = template_data["duration_minutes"]
        
        if "script_template" in template_data:
            project.script = template_data["script_template"]
        
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
