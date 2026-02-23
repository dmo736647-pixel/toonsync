"""协作功能属性测试"""
import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.collaboration import CollaboratorRole
from app.services.collaboration import CollaborationService
from app.schemas.collaboration import InvitationCreate
from tests.factories import UserFactory, ProjectFactory
from tests.strategies import email_strategy


# Feature: short-drama-production-tool, Property 30: 团队协作邀请
@pytest.mark.asyncio
@given(
    invitee_email=email_strategy,
    role=st.sampled_from(list(CollaboratorRole)),
)
@settings(max_examples=100, deadline=None)
async def test_property_30_team_collaboration_invitation(
    invitee_email: str,
    role: CollaboratorRole,
    db_session: AsyncSession
):
    """
    属性30：团队协作邀请
    
    对于任意邀请请求，系统应发送邀请并授予指定的权限级别
    
    **验证：需求8.3**
    
    测试策略：
    1. 使用随机生成的邮箱和角色
    2. 项目所有者发送邀请
    3. 验证邀请创建成功
    4. 验证邀请包含正确的权限级别
    """
    # 创建项目所有者和项目
    owner = UserFactory.build()
    db_session.add(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    project = ProjectFactory.build(user_id=owner.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # 发送邀请
    service = CollaborationService(db_session)
    invitation_data = InvitationCreate(
        email=invitee_email,
        role=role
    )
    
    invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
    
    # 验证邀请创建成功
    assert invitation is not None, "邀请应该创建成功"
    assert invitation.project_id == project.id, "邀请应关联到正确的项目"
    assert invitation.inviter_id == owner.id, "邀请应记录正确的邀请者"
    assert invitation.invitee_email == invitee_email, "邀请应包含正确的被邀请者邮箱"
    assert invitation.role == role, f"邀请应授予指定的权限级别 {role}"
    assert invitation.created_at is not None, "邀请应有创建时间"


@pytest.mark.asyncio
@given(
    role=st.sampled_from(list(CollaboratorRole)),
)
@settings(max_examples=50, deadline=None)
async def test_property_30_invitation_permission_levels(
    role: CollaboratorRole,
    db_session: AsyncSession
):
    """
    属性30：邀请权限级别验证
    
    对于任意权限级别的邀请，系统应正确授予该权限
    
    **验证：需求8.3**
    
    测试策略：
    1. 测试所有可能的权限级别（viewer, editor, admin）
    2. 验证邀请被接受后，协作者获得正确的权限
    """
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
        role=role
    )
    invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
    
    # 接受邀请
    collaborator = await service.accept_invitation(invitation.id, invitee.id)
    
    # 验证协作者获得正确的权限
    assert collaborator is not None, "协作者应该创建成功"
    assert collaborator.role == role, f"协作者应该获得 {role} 权限"
    assert collaborator.user_id == invitee.id, "协作者应关联到正确的用户"
    assert collaborator.project_id == project.id, "协作者应关联到正确的项目"


# Feature: short-drama-production-tool, Property 31: 并发编辑数据一致性
@pytest.mark.asyncio
@given(
    update_delay_seconds=st.integers(min_value=0, max_value=5),
)
@settings(max_examples=50, deadline=None)
async def test_property_31_concurrent_edit_data_consistency(
    update_delay_seconds: int,
    db_session: AsyncSession
):
    """
    属性31：并发编辑数据一致性
    
    对于任意多用户同时编辑的项目，系统应防止数据冲突并保持数据一致性
    
    **验证：需求8.4**
    
    测试策略：
    1. 创建项目和多个协作者
    2. 模拟并发编辑场景（使用乐观锁）
    3. 验证系统能检测到编辑冲突
    4. 验证数据一致性得到保持
    """
    # 创建项目所有者和项目
    owner = UserFactory.build()
    db_session.add(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    project = ProjectFactory.build(user_id=owner.id, name="原始名称")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # 记录初始版本时间戳（用户1的视图）
    user1_last_known_version = project.updated_at
    
    # 模拟用户2的编辑（更新项目）
    project.name = "用户2更新的名称"
    await db_session.commit()
    await db_session.refresh(project)
    
    # 用户1尝试编辑时检测冲突
    service = CollaborationService(db_session)
    has_conflict = await service.check_edit_conflict(
        project.id,
        owner.id,
        user1_last_known_version
    )
    
    # 验证系统检测到冲突
    assert has_conflict is True, "系统应该检测到并发编辑冲突"
    
    # 验证数据一致性：项目应该保持用户2的更新
    await db_session.refresh(project)
    assert project.name == "用户2更新的名称", "数据应该保持一致性"


@pytest.mark.asyncio
@given(
    collaborator_count=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=30, deadline=None)
async def test_property_31_multiple_collaborators_consistency(
    collaborator_count: int,
    db_session: AsyncSession
):
    """
    属性31：多协作者数据一致性
    
    对于任意数量的协作者，系统应保持项目数据的一致性
    
    **验证：需求8.4**
    
    测试策略：
    1. 创建项目和多个协作者
    2. 验证所有协作者都能访问同一个项目
    3. 验证项目数据在所有协作者视图中保持一致
    """
    # 创建项目所有者和项目
    owner = UserFactory.build()
    db_session.add(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    project = ProjectFactory.build(user_id=owner.id, name="共享项目")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # 添加多个协作者
    service = CollaborationService(db_session)
    collaborator_ids = []
    
    for i in range(collaborator_count):
        # 创建协作者用户
        collab_user = UserFactory.build(email=f"collab{i}@example.com")
        db_session.add(collab_user)
        await db_session.commit()
        await db_session.refresh(collab_user)
        
        # 发送并接受邀请
        invitation_data = InvitationCreate(
            email=f"collab{i}@example.com",
            role=CollaboratorRole.EDITOR
        )
        invitation = await service.invite_collaborator(project.id, owner.id, invitation_data)
        collaborator = await service.accept_invitation(invitation.id, collab_user.id)
        
        collaborator_ids.append(collab_user.id)
    
    # 验证所有协作者都能访问项目
    for collab_id in collaborator_ids:
        has_access = await service._check_project_access(project.id, collab_id)
        assert has_access is True, f"协作者 {collab_id} 应该能访问项目"
    
    # 验证协作者列表一致性
    collaborators = await service.list_collaborators(project.id, owner.id)
    assert collaborators is not None, "应该能列出协作者"
    assert len(collaborators) == collaborator_count, \
        f"协作者数量应该是 {collaborator_count}"


@pytest.mark.asyncio
@given(
    project_name=st.text(min_size=1, max_size=50),
)
@settings(max_examples=50, deadline=None)
async def test_property_31_conflict_detection_accuracy(
    project_name: str,
    db_session: AsyncSession
):
    """
    属性31：冲突检测准确性
    
    对于任意项目更新，系统应准确检测是否存在编辑冲突
    
    **验证：需求8.4**
    
    测试策略：
    1. 测试无冲突场景（版本最新）
    2. 测试有冲突场景（版本过时）
    3. 验证检测结果的准确性
    """
    # 创建项目
    owner = UserFactory.build()
    db_session.add(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    project = ProjectFactory.build(user_id=owner.id, name=project_name)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    service = CollaborationService(db_session)
    
    # 场景1：使用当前版本，应该无冲突
    current_version = project.updated_at
    has_conflict = await service.check_edit_conflict(
        project.id,
        owner.id,
        current_version
    )
    assert has_conflict is False, "当前版本应该无冲突"
    
    # 场景2：更新项目后，旧版本应该有冲突
    old_version = project.updated_at
    project.name = f"{project_name}_updated"
    await db_session.commit()
    await db_session.refresh(project)
    
    has_conflict = await service.check_edit_conflict(
        project.id,
        owner.id,
        old_version
    )
    assert has_conflict is True, "旧版本应该检测到冲突"
