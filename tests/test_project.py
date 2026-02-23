"""项目管理单元测试"""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project, AspectRatio
from app.services.project import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate
from tests.factories import UserFactory, ProjectFactory


@pytest.mark.asyncio
class TestProjectCreation:
    """测试项目创建和ID分配"""
    
    async def test_create_project_with_valid_data(self, db_session: AsyncSession):
        """测试使用有效数据创建项目"""
        # 创建测试用户
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 创建项目
        service = ProjectService(db_session)
        project_data = ProjectCreate(
            name="测试项目",
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=2.5
        )
        
        project = await service.create_project(user.id, project_data)
        
        # 验证项目创建成功
        assert project.id is not None
        assert project.user_id == user.id
        assert project.name == "测试项目"
        assert project.aspect_ratio == AspectRatio.VERTICAL_9_16
        assert project.duration_minutes == 2.5
        assert project.created_at is not None
        assert project.updated_at is not None
    
    async def test_create_project_assigns_unique_id(self, db_session: AsyncSession):
        """测试每个项目分配唯一ID"""
        # 创建测试用户
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 创建多个项目
        service = ProjectService(db_session)
        project_ids = set()
        
        for i in range(5):
            project_data = ProjectCreate(name=f"项目{i}")
            project = await service.create_project(user.id, project_data)
            project_ids.add(project.id)
        
        # 验证所有ID都是唯一的
        assert len(project_ids) == 5
    
    async def test_create_project_with_default_aspect_ratio(self, db_session: AsyncSession):
        """测试创建项目时使用默认画面比例"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        service = ProjectService(db_session)
        project_data = ProjectCreate(name="默认比例项目")
        project = await service.create_project(user.id, project_data)
        
        # 验证默认比例为9:16
        assert project.aspect_ratio == AspectRatio.VERTICAL_9_16
    
    async def test_create_project_with_script(self, db_session: AsyncSession):
        """测试创建带剧本的项目"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        service = ProjectService(db_session)
        script_content = "场景1：室内，白天。角色A：你好！"
        project_data = ProjectCreate(
            name="带剧本的项目",
            script=script_content
        )
        project = await service.create_project(user.id, project_data)
        
        assert project.script == script_content


@pytest.mark.asyncio
class TestProjectList:
    """测试项目列表查询（分页、过滤）"""
    
    async def test_list_projects_empty(self, db_session: AsyncSession):
        """测试列出空项目列表"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        service = ProjectService(db_session)
        projects, total = await service.list_projects(user.id)
        
        assert projects == []
        assert total == 0
    
    async def test_list_projects_with_pagination(self, db_session: AsyncSession):
        """测试项目列表分页"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 创建10个项目
        service = ProjectService(db_session)
        for i in range(10):
            project_data = ProjectCreate(name=f"项目{i}")
            await service.create_project(user.id, project_data)
        
        # 测试第一页（5个项目）
        projects, total = await service.list_projects(user.id, page=1, page_size=5)
        assert len(projects) == 5
        assert total == 10
        
        # 测试第二页（5个项目）
        projects, total = await service.list_projects(user.id, page=2, page_size=5)
        assert len(projects) == 5
        assert total == 10
        
        # 测试第三页（0个项目）
        projects, total = await service.list_projects(user.id, page=3, page_size=5)
        assert len(projects) == 0
        assert total == 10
    
    async def test_list_projects_with_name_filter(self, db_session: AsyncSession):
        """测试项目名称过滤"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 创建不同名称的项目
        service = ProjectService(db_session)
        await service.create_project(user.id, ProjectCreate(name="微短剧A"))
        await service.create_project(user.id, ProjectCreate(name="微短剧B"))
        await service.create_project(user.id, ProjectCreate(name="动态漫C"))
        
        # 过滤包含"微短剧"的项目
        projects, total = await service.list_projects(user.id, name_filter="微短剧")
        assert len(projects) == 2
        assert total == 2
        assert all("微短剧" in p.name for p in projects)
        
        # 过滤包含"动态漫"的项目
        projects, total = await service.list_projects(user.id, name_filter="动态漫")
        assert len(projects) == 1
        assert total == 1
    
    async def test_list_projects_only_shows_user_projects(self, db_session: AsyncSession):
        """测试只显示当前用户的项目"""
        # 创建两个用户
        user1 = UserFactory.build()
        user2 = UserFactory.build()
        db_session.add_all([user1, user2])
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)
        
        # 为每个用户创建项目
        service = ProjectService(db_session)
        await service.create_project(user1.id, ProjectCreate(name="用户1的项目"))
        await service.create_project(user2.id, ProjectCreate(name="用户2的项目"))
        
        # 验证用户1只能看到自己的项目
        projects, total = await service.list_projects(user1.id)
        assert len(projects) == 1
        assert total == 1
        assert projects[0].name == "用户1的项目"
        
        # 验证用户2只能看到自己的项目
        projects, total = await service.list_projects(user2.id)
        assert len(projects) == 1
        assert total == 1
        assert projects[0].name == "用户2的项目"


@pytest.mark.asyncio
class TestProjectUpdate:
    """测试项目更新"""
    
    async def test_update_project_name(self, db_session: AsyncSession):
        """测试更新项目名称"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 创建项目
        service = ProjectService(db_session)
        project = await service.create_project(
            user.id,
            ProjectCreate(name="原始名称")
        )
        
        # 更新项目名称
        update_data = ProjectUpdate(name="新名称")
        updated_project = await service.update_project(project.id, user.id, update_data)
        
        assert updated_project is not None
        assert updated_project.name == "新名称"
        assert updated_project.id == project.id
    
    async def test_update_project_aspect_ratio(self, db_session: AsyncSession):
        """测试更新项目画面比例"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        service = ProjectService(db_session)
        project = await service.create_project(
            user.id,
            ProjectCreate(name="测试项目", aspect_ratio=AspectRatio.VERTICAL_9_16)
        )
        
        # 更新画面比例
        update_data = ProjectUpdate(aspect_ratio=AspectRatio.HORIZONTAL_16_9)
        updated_project = await service.update_project(project.id, user.id, update_data)
        
        assert updated_project.aspect_ratio == AspectRatio.HORIZONTAL_16_9
    
    async def test_update_project_partial_fields(self, db_session: AsyncSession):
        """测试部分字段更新"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        service = ProjectService(db_session)
        project = await service.create_project(
            user.id,
            ProjectCreate(
                name="原始项目",
                aspect_ratio=AspectRatio.VERTICAL_9_16,
                duration_minutes=2.0
            )
        )
        
        # 只更新时长
        update_data = ProjectUpdate(duration_minutes=3.5)
        updated_project = await service.update_project(project.id, user.id, update_data)
        
        # 验证只有时长被更新，其他字段保持不变
        assert updated_project.duration_minutes == 3.5
        assert updated_project.name == "原始项目"
        assert updated_project.aspect_ratio == AspectRatio.VERTICAL_9_16
    
    async def test_update_nonexistent_project(self, db_session: AsyncSession):
        """测试更新不存在的项目"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        service = ProjectService(db_session)
        fake_project_id = uuid4()
        update_data = ProjectUpdate(name="新名称")
        
        result = await service.update_project(fake_project_id, user.id, update_data)
        assert result is None


@pytest.mark.asyncio
class TestProjectDelete:
    """测试项目删除"""
    
    async def test_delete_project(self, db_session: AsyncSession):
        """测试删除项目"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 创建项目
        service = ProjectService(db_session)
        project = await service.create_project(
            user.id,
            ProjectCreate(name="待删除项目")
        )
        project_id = project.id
        
        # 删除项目
        success = await service.delete_project(project_id, user.id)
        assert success is True
        
        # 验证项目已被删除
        deleted_project = await service.get_project(project_id, user.id)
        assert deleted_project is None
    
    async def test_delete_nonexistent_project(self, db_session: AsyncSession):
        """测试删除不存在的项目"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        service = ProjectService(db_session)
        fake_project_id = uuid4()
        
        success = await service.delete_project(fake_project_id, user.id)
        assert success is False


@pytest.mark.asyncio
class TestProjectPermissions:
    """测试项目权限验证"""
    
    async def test_user_cannot_access_other_user_project(self, db_session: AsyncSession):
        """测试用户无法访问其他用户的项目"""
        # 创建两个用户
        user1 = UserFactory.build()
        user2 = UserFactory.build()
        db_session.add_all([user1, user2])
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)
        
        # 用户1创建项目
        service = ProjectService(db_session)
        project = await service.create_project(
            user1.id,
            ProjectCreate(name="用户1的项目")
        )
        
        # 用户2尝试访问用户1的项目
        result = await service.get_project(project.id, user2.id)
        assert result is None
    
    async def test_user_cannot_update_other_user_project(self, db_session: AsyncSession):
        """测试用户无法更新其他用户的项目"""
        user1 = UserFactory.build()
        user2 = UserFactory.build()
        db_session.add_all([user1, user2])
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)
        
        service = ProjectService(db_session)
        project = await service.create_project(
            user1.id,
            ProjectCreate(name="用户1的项目")
        )
        
        # 用户2尝试更新用户1的项目
        update_data = ProjectUpdate(name="恶意修改")
        result = await service.update_project(project.id, user2.id, update_data)
        assert result is None
    
    async def test_user_cannot_delete_other_user_project(self, db_session: AsyncSession):
        """测试用户无法删除其他用户的项目"""
        user1 = UserFactory.build()
        user2 = UserFactory.build()
        db_session.add_all([user1, user2])
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)
        
        service = ProjectService(db_session)
        project = await service.create_project(
            user1.id,
            ProjectCreate(name="用户1的项目")
        )
        
        # 用户2尝试删除用户1的项目
        success = await service.delete_project(project.id, user2.id)
        assert success is False
        
        # 验证项目仍然存在
        existing_project = await service.get_project(project.id, user1.id)
        assert existing_project is not None
