"""版本管理属性测试"""
import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.collaboration import VersionService, TemplateService
from app.schemas.collaboration import VersionCreate, TemplateCreate
from tests.factories import UserFactory, ProjectFactory


# Feature: short-drama-production-tool, Property 32: 自动保存和版本历史
@pytest.mark.asyncio
@given(
    version_description=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    modification_count=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=50, deadline=None)
async def test_property_32_auto_save_and_version_history(
    version_description: str,
    modification_count: int,
    db_session: AsyncSession
):
    """
    属性32：自动保存和版本历史
    
    对于任意项目修改，系统应自动保存更改并保留最近30天的版本历史
    
    **验证：需求8.5**
    
    测试策略：
    1. 创建项目并进行多次修改
    2. 每次修改后创建版本
    3. 验证所有版本都被保存
    4. 验证版本历史可以被检索（30天内）
    """
    # 创建项目
    owner = UserFactory.build()
    db_session.add(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    project = ProjectFactory.build(user_id=owner.id, name="测试项目")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # 进行多次修改并创建版本
    service = VersionService(db_session)
    created_versions = []
    
    for i in range(modification_count):
        # 修改项目
        project.name = f"测试项目_修改{i+1}"
        await db_session.commit()
        await db_session.refresh(project)
        
        # 创建版本
        version_data = VersionCreate(
            description=f"{version_description}_{i+1}" if version_description else None
        )
        version = await service.create_version(project.id, owner.id, version_data)
        created_versions.append(version)
    
    # 验证所有版本都被保存
    assert len(created_versions) == modification_count, \
        f"应该创建 {modification_count} 个版本"
    
    # 验证版本号递增
    for i, version in enumerate(created_versions):
        assert version.version_number == i + 1, \
            f"版本号应该是 {i + 1}"
    
    # 验证可以检索30天内的版本历史
    versions = await service.list_versions(project.id, owner.id, days=30)
    assert versions is not None, "应该能检索版本历史"
    assert len(versions) == modification_count, \
        f"应该检索到 {modification_count} 个版本"
    
    # 验证版本按降序排列
    for i in range(len(versions) - 1):
        assert versions[i].version_number > versions[i + 1].version_number, \
            "版本应该按版本号降序排列"


@pytest.mark.asyncio
@given(
    days_to_keep=st.integers(min_value=1, max_value=90),
)
@settings(max_examples=30, deadline=None)
async def test_property_32_version_history_retention(
    days_to_keep: int,
    db_session: AsyncSession
):
    """
    属性32：版本历史保留期限
    
    对于任意保留天数设置，系统应正确过滤版本历史
    
    **验证：需求8.5**
    
    测试策略：
    1. 创建项目和多个版本
    2. 使用不同的保留天数查询版本历史
    3. 验证返回的版本符合时间范围
    """
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
    version_count = 5
    
    for i in range(version_count):
        version_data = VersionCreate(description=f"版本{i+1}")
        await service.create_version(project.id, owner.id, version_data)
    
    # 查询指定天数内的版本
    versions = await service.list_versions(project.id, owner.id, days=days_to_keep)
    
    # 验证返回的版本
    assert versions is not None, "应该能检索版本历史"
    assert len(versions) <= version_count, "返回的版本数不应超过创建的版本数"
    
    # 验证所有版本都在指定天数内（由于刚创建，应该都在范围内）
    assert len(versions) == version_count, \
        f"所有 {version_count} 个版本都应该在 {days_to_keep} 天内"


# Feature: short-drama-production-tool, Property 33: 项目模板复用
@pytest.mark.asyncio
@given(
    template_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    is_public=st.booleans(),
)
@settings(max_examples=50, deadline=None)
async def test_property_33_project_template_reuse(
    template_name: str,
    is_public: bool,
    db_session: AsyncSession
):
    """
    属性33：项目模板复用
    
    对于任意保存的项目模板，系统应允许创作者复用模板，正确应用模板中的设置
    
    **验证：需求8.6**
    
    测试策略：
    1. 从源项目创建模板
    2. 将模板应用到新项目
    3. 验证模板设置被正确应用
    4. 验证源项目和目标项目的设置一致
    """
    # 创建用户
    owner = UserFactory.build()
    db_session.add(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    # 创建源项目（包含特定设置）
    from app.models.project import AspectRatio
    source_project = ProjectFactory.build(
        user_id=owner.id,
        name="源项目",
        aspect_ratio=AspectRatio.HORIZONTAL_16_9,
        duration_minutes=5.0,
        script="这是模板剧本"
    )
    db_session.add(source_project)
    await db_session.commit()
    await db_session.refresh(source_project)
    
    # 从源项目创建模板
    template_service = TemplateService(db_session)
    template_data = TemplateCreate(
        name=template_name,
        description="测试模板",
        is_public=is_public
    )
    template = await template_service.create_template(
        source_project.id,
        owner.id,
        template_data
    )
    
    # 验证模板创建成功
    assert template is not None, "模板应该创建成功"
    assert template.name == template_name, "模板名称应该正确"
    
    # 创建目标项目（使用不同的设置）
    target_project = ProjectFactory.build(
        user_id=owner.id,
        name="目标项目",
        aspect_ratio=AspectRatio.VERTICAL_9_16,
        duration_minutes=2.0,
        script="原始剧本"
    )
    db_session.add(target_project)
    await db_session.commit()
    await db_session.refresh(target_project)
    
    # 应用模板到目标项目
    updated_project = await template_service.apply_template(
        template.id,
        target_project.id,
        owner.id
    )
    
    # 验证模板应用成功
    assert updated_project is not None, "模板应该应用成功"
    
    # 验证模板设置被正确应用
    assert updated_project.aspect_ratio == source_project.aspect_ratio, \
        "画面比例应该与源项目一致"
    assert updated_project.duration_minutes == source_project.duration_minutes, \
        "时长应该与源项目一致"
    assert updated_project.script == source_project.script, \
        "剧本应该与源项目一致"


@pytest.mark.asyncio
@given(
    project_count=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=30, deadline=None)
async def test_property_33_template_reuse_multiple_projects(
    project_count: int,
    db_session: AsyncSession
):
    """
    属性33：模板可重复应用到多个项目
    
    对于任意模板，系统应允许将其应用到多个不同的项目
    
    **验证：需求8.6**
    
    测试策略：
    1. 创建一个模板
    2. 将模板应用到多个项目
    3. 验证所有项目都正确应用了模板设置
    """
    # 创建用户
    owner = UserFactory.build()
    db_session.add(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    # 创建源项目和模板
    from app.models.project import AspectRatio
    source_project = ProjectFactory.build(
        user_id=owner.id,
        name="模板源项目",
        aspect_ratio=AspectRatio.SQUARE_1_1,
        duration_minutes=3.0
    )
    db_session.add(source_project)
    await db_session.commit()
    await db_session.refresh(source_project)
    
    template_service = TemplateService(db_session)
    template_data = TemplateCreate(
        name="共享模板",
        is_public=False
    )
    template = await template_service.create_template(
        source_project.id,
        owner.id,
        template_data
    )
    
    # 创建多个目标项目并应用模板
    updated_projects = []
    
    for i in range(project_count):
        target_project = ProjectFactory.build(
            user_id=owner.id,
            name=f"目标项目{i+1}",
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=1.0
        )
        db_session.add(target_project)
        await db_session.commit()
        await db_session.refresh(target_project)
        
        # 应用模板
        updated_project = await template_service.apply_template(
            template.id,
            target_project.id,
            owner.id
        )
        updated_projects.append(updated_project)
    
    # 验证所有项目都正确应用了模板
    assert len(updated_projects) == project_count, \
        f"应该有 {project_count} 个项目应用了模板"
    
    for project in updated_projects:
        assert project is not None, "项目应该更新成功"
        assert project.aspect_ratio == source_project.aspect_ratio, \
            "所有项目的画面比例应该与模板一致"
        assert project.duration_minutes == source_project.duration_minutes, \
            "所有项目的时长应该与模板一致"


@pytest.mark.asyncio
@given(
    template_description=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
)
@settings(max_examples=50, deadline=None)
async def test_property_33_template_settings_preservation(
    template_description: str,
    db_session: AsyncSession
):
    """
    属性33：模板设置保留
    
    对于任意模板，系统应正确保存和恢复模板中的所有设置
    
    **验证：需求8.6**
    
    测试策略：
    1. 创建包含各种设置的项目
    2. 从项目创建模板
    3. 应用模板到新项目
    4. 验证所有设置都被正确保留和应用
    """
    # 创建用户
    owner = UserFactory.build()
    db_session.add(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    # 创建源项目（包含完整设置）
    from app.models.project import AspectRatio
    source_project = ProjectFactory.build(
        user_id=owner.id,
        name="完整设置项目",
        aspect_ratio=AspectRatio.HORIZONTAL_16_9,
        duration_minutes=4.5,
        script="完整的剧本内容"
    )
    db_session.add(source_project)
    await db_session.commit()
    await db_session.refresh(source_project)
    
    # 创建模板
    template_service = TemplateService(db_session)
    template_data = TemplateCreate(
        name="完整模板",
        description=template_description,
        is_public=False
    )
    template = await template_service.create_template(
        source_project.id,
        owner.id,
        template_data
    )
    
    # 验证模板保存了描述
    if template_description:
        assert template.description == template_description, \
            "模板描述应该被正确保存"
    
    # 创建空白项目
    target_project = ProjectFactory.build(
        user_id=owner.id,
        name="空白项目"
    )
    db_session.add(target_project)
    await db_session.commit()
    await db_session.refresh(target_project)
    
    # 应用模板
    updated_project = await template_service.apply_template(
        template.id,
        target_project.id,
        owner.id
    )
    
    # 验证所有设置都被正确应用
    assert updated_project is not None, "模板应该应用成功"
    assert updated_project.aspect_ratio == source_project.aspect_ratio, \
        "画面比例应该被保留"
    assert updated_project.duration_minutes == source_project.duration_minutes, \
        "时长应该被保留"
    assert updated_project.script == source_project.script, \
        "剧本内容应该被保留"
