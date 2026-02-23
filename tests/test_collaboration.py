"""协作功能单元测试"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collaboration import CollaboratorRole, InvitationStatus
from app.services.collaboration import CollaborationService, VersionService, TemplateService
from app.schemas.collaboration import InvitationCreate, CollaboratorUpdate, VersionCreate, TemplateCreate
from tests.factories import UserFactory, ProjectFactory


@pytest.mark.asyncio
class TestTeamInvitation:
    """测试团队成员邀请流程"""
    
    async def test_invite_collaborator_success(self, db_session: AsyncSession):
        """测试成功邀请协作者"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 邀请协作者
        service = CollaborationService(db_session)
        invitation_data = InvitationCreate(
            email="collaborator@example.com",
            role=CollaboratorRole.EDITOR
        )
        
        invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
        
        assert invitation is not None
        assert invitation.project_id == project.id
        assert invitation.inviter_id == owner.id
        assert invitation.invitee_email == "collaborator@example.com"
        assert invitation.role == CollaboratorRole.EDITOR
        assert invitation.status == InvitationStatus.PENDING
    
    async def test_invite_collaborator_without_permission(self, db_session: AsyncSession):
        """测试无权限用户无法邀请协作者"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        other_user = UserFactory.build()
        db_session.add_all([owner, other_user])
        await db_session.commit()
        await db_session.refresh(owner)
        await db_session.refresh(other_user)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 其他用户尝试邀请协作者
        service = CollaborationService(db_session)
        invitation_data = InvitationCreate(
            email="collaborator@example.com",
            role=CollaboratorRole.EDITOR
        )
        
        invitation = await service.invite_collaborator(project.id, other_user.id, invitation_data)
        
        assert invitation is None
    
    async def test_accept_invitation_success(self, db_session: AsyncSession):
        """测试成功接受邀请"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 创建被邀请用户
        invitee = UserFactory.build(email="invitee@example.com")
        db_session.add(invitee)
        await db_session.commit()
        await db_session.refresh(invitee)
        
        # 发送邀请
        service = CollaborationService(db_session)
        invitation_data = InvitationCreate(
            email="invitee@example.com",
            role=CollaboratorRole.EDITOR
        )
        invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
        
        # 接受邀请
        collaborator = await service.accept_invitation(invitation.id, invitee.id)
        
        assert collaborator is not None
        assert collaborator.project_id == project.id
        assert collaborator.user_id == invitee.id
        assert collaborator.role == CollaboratorRole.EDITOR
    
    async def test_accept_invitation_with_wrong_email(self, db_session: AsyncSession):
        """测试邮箱不匹配时无法接受邀请"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 创建用户（邮箱不匹配）
        wrong_user = UserFactory.build(email="wrong@example.com")
        db_session.add(wrong_user)
        await db_session.commit()
        await db_session.refresh(wrong_user)
        
        # 发送邀请
        service = CollaborationService(db_session)
        invitation_data = InvitationCreate(
            email="correct@example.com",
            role=CollaboratorRole.EDITOR
        )
        invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
        
        # 尝试接受邀请
        collaborator = await service.accept_invitation(invitation.id, wrong_user.id)
        
        assert collaborator is None


@pytest.mark.asyncio
class TestPermissionLevels:
    """测试权限级别验证"""
    
    async def test_viewer_cannot_invite(self, db_session: AsyncSession):
        """测试查看者无法邀请新成员"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        viewer = UserFactory.build(email="viewer@example.com")
        db_session.add_all([owner, viewer])
        await db_session.commit()
        await db_session.refresh(owner)
        await db_session.refresh(viewer)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 添加查看者
        service = CollaborationService(db_session)
        invitation_data = InvitationCreate(
            email="viewer@example.com",
            role=CollaboratorRole.VIEWER
        )
        invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
        await service.accept_invitation(invitation.id, viewer.id)
        
        # 查看者尝试邀请新成员
        new_invitation_data = InvitationCreate(
            email="newmember@example.com",
            role=CollaboratorRole.EDITOR
        )
        result = await service.invite_collaborator(project.id, viewer.id, new_invitation_data)
        
        assert result is None
    
    async def test_admin_can_invite(self, db_session: AsyncSession):
        """测试管理员可以邀请新成员"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        admin = UserFactory.build(email="admin@example.com")
        db_session.add_all([owner, admin])
        await db_session.commit()
        await db_session.refresh(owner)
        await db_session.refresh(admin)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 添加管理员
        service = CollaborationService(db_session)
        invitation_data = InvitationCreate(
            email="admin@example.com",
            role=CollaboratorRole.ADMIN
        )
        invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
        await service.accept_invitation(invitation.id, admin.id)
        
        # 管理员邀请新成员
        new_invitation_data = InvitationCreate(
            email="newmember@example.com",
            role=CollaboratorRole.EDITOR
        )
        result = await service.invite_collaborator(project.id, admin.id, new_invitation_data)
        
        assert result is not None
    
    async def test_update_collaborator_role(self, db_session: AsyncSession):
        """测试更新协作者角色"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        collaborator_user = UserFactory.build(email="collab@example.com")
        db_session.add_all([owner, collaborator_user])
        await db_session.commit()
        await db_session.refresh(owner)
        await db_session.refresh(collaborator_user)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 添加协作者
        service = CollaborationService(db_session)
        invitation_data = InvitationCreate(
            email="collab@example.com",
            role=CollaboratorRole.VIEWER
        )
        invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
        collaborator = await service.accept_invitation(invitation.id, collaborator_user.id)
        
        # 更新角色
        update_data = CollaboratorUpdate(role=CollaboratorRole.EDITOR)
        updated_collaborator = await service.update_collaborator_role(
            collaborator.id,
            owner.id,
            update_data
        )
        
        assert updated_collaborator is not None
        assert updated_collaborator.role == CollaboratorRole.EDITOR


@pytest.mark.asyncio
class TestConcurrentEditConflict:
    """测试并发编辑冲突检测"""
    
    async def test_detect_edit_conflict(self, db_session: AsyncSession):
        """测试检测编辑冲突"""
        # 创建项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 记录初始版本时间
        initial_version = project.updated_at
        
        # 模拟另一个用户的编辑（更新项目）
        project.name = "更新后的名称"
        await db_session.commit()
        await db_session.refresh(project)
        
        # 检测冲突
        service = CollaborationService(db_session)
        has_conflict = await service.check_edit_conflict(
            project.id,
            owner.id,
            initial_version
        )
        
        assert has_conflict is True
    
    async def test_no_conflict_when_up_to_date(self, db_session: AsyncSession):
        """测试当版本最新时无冲突"""
        # 创建项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 使用当前版本时间
        current_version = project.updated_at
        
        # 检测冲突
        service = CollaborationService(db_session)
        has_conflict = await service.check_edit_conflict(
            project.id,
            owner.id,
            current_version
        )
        
        assert has_conflict is False


@pytest.mark.asyncio
class TestCollaboratorList:
    """测试协作者列表查询"""
    
    async def test_list_collaborators(self, db_session: AsyncSession):
        """测试列出所有协作者"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 添加多个协作者
        service = CollaborationService(db_session)
        collaborator_emails = ["collab1@example.com", "collab2@example.com", "collab3@example.com"]
        
        for email in collaborator_emails:
            user = UserFactory.build(email=email)
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            
            invitation_data = InvitationCreate(email=email, role=CollaboratorRole.EDITOR)
            invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
            await service.accept_invitation(invitation.id, user.id)
        
        # 列出协作者
        collaborators = await service.list_collaborators(project.id, owner.id)
        
        assert collaborators is not None
        assert len(collaborators) == 3
    
    async def test_list_collaborators_without_permission(self, db_session: AsyncSession):
        """测试无权限用户无法查看协作者列表"""
        # 创建项目所有者和项目
        owner = UserFactory.build()
        other_user = UserFactory.build()
        db_session.add_all([owner, other_user])
        await db_session.commit()
        await db_session.refresh(owner)
        await db_session.refresh(other_user)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 其他用户尝试查看协作者列表
        service = CollaborationService(db_session)
        collaborators = await service.list_collaborators(project.id, other_user.id)
        
        assert collaborators is None


@pytest.mark.asyncio
class TestVersionManagement:
    """测试版本管理"""
    
    async def test_create_version(self, db_session: AsyncSession):
        """测试创建项目版本"""
        # 创建项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id, name="原始项目")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 创建版本
        service = VersionService(db_session)
        version_data = VersionCreate(description="初始版本")
        version = await service.create_version(project.id, owner.id, version_data)
        
        assert version is not None
        assert version.project_id == project.id
        assert version.version_number == 1
        assert version.description == "初始版本"
        assert version.created_by == owner.id
    
    async def test_list_versions(self, db_session: AsyncSession):
        """测试列出版本历史"""
        # 创建项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 创建多个版本
        service = VersionService(db_session)
        for i in range(3):
            version_data = VersionCreate(description=f"版本{i+1}")
            await service.create_version(project.id, owner.id, version_data)
        
        # 列出版本
        versions = await service.list_versions(project.id, owner.id, days=30)
        
        assert versions is not None
        assert len(versions) == 3
        # 验证按版本号降序排列
        assert versions[0].version_number == 3
        assert versions[1].version_number == 2
        assert versions[2].version_number == 1


@pytest.mark.asyncio
class TestTemplateManagement:
    """测试模板管理"""
    
    async def test_create_template(self, db_session: AsyncSession):
        """测试创建项目模板"""
        # 创建项目
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        project = ProjectFactory.build(user_id=owner.id, name="模板项目")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # 创建模板
        service = TemplateService(db_session)
        template_data = TemplateCreate(
            name="我的模板",
            description="测试模板",
            is_public=False
        )
        template = await service.create_template(project.id, owner.id, template_data)
        
        assert template is not None
        assert template.name == "我的模板"
        assert template.description == "测试模板"
        assert template.created_by == owner.id
    
    async def test_apply_template(self, db_session: AsyncSession):
        """测试应用模板到项目"""
        # 创建源项目和模板
        owner = UserFactory.build()
        db_session.add(owner)
        await db_session.commit()
        await db_session.refresh(owner)
        
        source_project = ProjectFactory.build(
            user_id=owner.id,
            name="源项目",
            duration_minutes=3.0
        )
        db_session.add(source_project)
        await db_session.commit()
        await db_session.refresh(source_project)
        
        service = TemplateService(db_session)
        template_data = TemplateCreate(name="模板", is_public=False)
        template = await service.create_template(source_project.id, owner.id, template_data)
        
        # 创建目标项目
        target_project = ProjectFactory.build(
            user_id=owner.id,
            name="目标项目",
            duration_minutes=1.0
        )
        db_session.add(target_project)
        await db_session.commit()
        await db_session.refresh(target_project)
        
        # 应用模板
        updated_project = await service.apply_template(template.id, target_project.id, owner.id)
        
        assert updated_project is not None
        assert updated_project.duration_minutes == 3.0  # 应用了模板的时长
