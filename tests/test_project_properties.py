"""项目管理属性测试"""
import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import AspectRatio
from app.services.project import ProjectService
from app.schemas.project import ProjectCreate
from tests.factories import UserFactory
from tests.strategies import project_name_strategy, aspect_ratio_strategy, duration_minutes_strategy


# Feature: short-drama-production-tool, Property 29: 项目唯一标识
@pytest.mark.asyncio
@given(
    project_name=project_name_strategy(),
    aspect_ratio=aspect_ratio_strategy(),
    duration_minutes=duration_minutes_strategy(),
)
@settings(max_examples=100, deadline=None)
async def test_property_29_project_unique_id(
    project_name: str,
    aspect_ratio: AspectRatio,
    duration_minutes: float,
    db_session: AsyncSession
):
    """
    属性29：项目唯一标识
    
    对于任意新创建的项目，系统应分配唯一的项目ID并初始化项目工作区
    
    **验证：需求8.1**
    
    测试策略：
    1. 使用随机生成的项目名称、画面比例和时长
    2. 创建多个项目
    3. 验证每个项目都有唯一的ID
    4. 验证项目工作区正确初始化（包含必要字段）
    """
    # 创建测试用户
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建项目服务
    service = ProjectService(db_session)
    
    # 创建多个项目以测试唯一性
    project_ids = set()
    projects = []
    
    for i in range(3):
        project_data = ProjectCreate(
            name=f"{project_name}_{i}",
            aspect_ratio=aspect_ratio,
            duration_minutes=duration_minutes
        )
        
        project = await service.create_project(user.id, project_data)
        projects.append(project)
        
        # 验证项目ID存在且唯一
        assert project.id is not None, "项目ID不应为None"
        assert project.id not in project_ids, f"项目ID {project.id} 不唯一"
        project_ids.add(project.id)
        
        # 验证项目工作区初始化
        assert project.user_id == user.id, "项目应关联到正确的用户"
        assert project.name == f"{project_name}_{i}", "项目名称应正确设置"
        assert project.aspect_ratio == aspect_ratio, "画面比例应正确设置"
        assert project.duration_minutes == duration_minutes, "时长应正确设置"
        assert project.created_at is not None, "创建时间应被设置"
        assert project.updated_at is not None, "更新时间应被设置"
    
    # 验证所有项目ID都是唯一的
    assert len(project_ids) == 3, "应该有3个唯一的项目ID"
    
    # 验证可以通过ID检索项目
    for project in projects:
        retrieved_project = await service.get_project(project.id, user.id)
        assert retrieved_project is not None, f"应该能够检索项目 {project.id}"
        assert retrieved_project.id == project.id, "检索的项目ID应匹配"


@pytest.mark.asyncio
@given(
    project_count=st.integers(min_value=1, max_value=10),
    project_name_prefix=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
)
@settings(max_examples=50, deadline=None)
async def test_property_29_multiple_projects_unique_ids(
    project_count: int,
    project_name_prefix: str,
    db_session: AsyncSession
):
    """
    属性29：项目唯一标识（批量测试）
    
    对于任意数量的新创建项目，系统应为每个项目分配唯一的ID
    
    **验证：需求8.1**
    
    测试策略：
    1. 创建任意数量（1-10个）的项目
    2. 验证所有项目ID都是唯一的
    3. 验证每个项目都可以独立访问
    """
    # 创建测试用户
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建项目服务
    service = ProjectService(db_session)
    
    # 创建多个项目
    project_ids = set()
    
    for i in range(project_count):
        project_data = ProjectCreate(
            name=f"{project_name_prefix}_{i}",
            aspect_ratio=AspectRatio.VERTICAL_9_16
        )
        
        project = await service.create_project(user.id, project_data)
        
        # 验证ID唯一性
        assert project.id not in project_ids, f"项目ID {project.id} 重复"
        project_ids.add(project.id)
    
    # 验证所有ID都是唯一的
    assert len(project_ids) == project_count, f"应该有 {project_count} 个唯一的项目ID"


@pytest.mark.asyncio
@given(
    project_name=project_name_strategy(),
    aspect_ratio=aspect_ratio_strategy(),
)
@settings(max_examples=100, deadline=None)
async def test_property_29_project_workspace_initialization(
    project_name: str,
    aspect_ratio: AspectRatio,
    db_session: AsyncSession
):
    """
    属性29：项目工作区初始化
    
    对于任意新创建的项目，系统应正确初始化项目工作区
    
    **验证：需求8.1**
    
    测试策略：
    1. 创建项目
    2. 验证所有必要字段都被正确初始化
    3. 验证项目可以被检索和访问
    """
    # 创建测试用户
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建项目
    service = ProjectService(db_session)
    project_data = ProjectCreate(
        name=project_name,
        aspect_ratio=aspect_ratio
    )
    
    project = await service.create_project(user.id, project_data)
    
    # 验证项目工作区初始化
    assert project.id is not None, "项目ID应被分配"
    assert project.user_id == user.id, "项目应关联到用户"
    assert project.name == project_name, "项目名称应正确"
    assert project.aspect_ratio == aspect_ratio, "画面比例应正确"
    assert project.created_at is not None, "创建时间应被设置"
    assert project.updated_at is not None, "更新时间应被设置"
    
    # 验证项目可以被检索
    retrieved_project = await service.get_project(project.id, user.id)
    assert retrieved_project is not None, "项目应该可以被检索"
    assert retrieved_project.id == project.id, "检索的项目应该是同一个项目"
    
    # 验证项目出现在用户的项目列表中
    projects, total = await service.list_projects(user.id)
    assert total == 1, "用户应该有1个项目"
    assert projects[0].id == project.id, "列表中的项目应该是刚创建的项目"


@pytest.mark.asyncio
@given(
    user_count=st.integers(min_value=2, max_value=5),
    projects_per_user=st.integers(min_value=1, max_value=3),
)
@settings(max_examples=30, deadline=None)
async def test_property_29_project_ids_unique_across_users(
    user_count: int,
    projects_per_user: int,
    db_session: AsyncSession
):
    """
    属性29：跨用户的项目ID唯一性
    
    对于任意多个用户创建的项目，所有项目ID应该是全局唯一的
    
    **验证：需求8.1**
    
    测试策略：
    1. 创建多个用户
    2. 每个用户创建多个项目
    3. 验证所有项目ID在全局范围内都是唯一的
    """
    service = ProjectService(db_session)
    all_project_ids = set()
    
    # 为每个用户创建项目
    for user_idx in range(user_count):
        # 创建用户
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 为该用户创建项目
        for project_idx in range(projects_per_user):
            project_data = ProjectCreate(
                name=f"用户{user_idx}_项目{project_idx}"
            )
            project = await service.create_project(user.id, project_data)
            
            # 验证ID全局唯一
            assert project.id not in all_project_ids, \
                f"项目ID {project.id} 在全局范围内重复"
            all_project_ids.add(project.id)
    
    # 验证总数
    expected_total = user_count * projects_per_user
    assert len(all_project_ids) == expected_total, \
        f"应该有 {expected_total} 个唯一的项目ID"
