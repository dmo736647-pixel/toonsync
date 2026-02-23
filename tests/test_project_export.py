"""项目导出功能单元测试"""
import pytest
import zipfile
import json
from io import BytesIO
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, SubscriptionTier
from app.models.project import Project
from app.models.character import Character
from app.services.project_export import ProjectExportService


class TestProjectExportService:
    """项目导出服务测试"""
    
    @pytest.fixture
    def db_session(self):
        """创建数据库会话"""
        db = next(get_db())
        yield db
        db.close()
    
    @pytest.fixture
    def test_user(self, db_session):
        """创建测试用户"""
        user = User(
            email="test_export@example.com",
            password_hash="hashed_password",
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            remaining_quota_minutes=50.0
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        yield user
        # 清理
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()
    
    @pytest.fixture
    def test_project(self, db_session, test_user):
        """创建测试项目"""
        project = Project(
            user_id=test_user.id,
            name="Test Export Project",
            aspect_ratio="9:16",
            duration_minutes=2.5,
            script="Test script content"
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        yield project
        # 清理
        db_session.query(Project).filter(Project.id == project.id).delete()
        db_session.commit()
    
    def test_export_project_metadata(self, db_session, test_project):
        """
        测试导出项目元数据
        
        需求：11.6
        """
        export_service = ProjectExportService(db_session)
        
        # 导出项目（不包含媒体）
        zip_buffer = export_service.export_project(
            str(test_project.id),
            include_media=False
        )
        
        # 验证ZIP文件
        assert isinstance(zip_buffer, BytesIO), "应该返回BytesIO对象"
        
        # 读取ZIP内容
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            # 验证包含project.json
            assert "project.json" in zip_file.namelist(), "应该包含project.json"
            
            # 读取项目元数据
            project_json = zip_file.read("project.json").decode('utf-8')
            project_data = json.loads(project_json)
            
            # 验证元数据内容
            assert project_data["name"] == test_project.name
            assert project_data["aspect_ratio"] == test_project.aspect_ratio
            assert project_data["script"] == test_project.script
    
    def test_export_project_with_characters(self, db_session, test_project):
        """
        测试导出包含角色的项目
        
        需求：11.6
        """
        # 创建测试角色
        character = Character(
            project_id=test_project.id,
            name="Test Character",
            reference_image_url="/storage/test/character.jpg",
            style="anime"
        )
        db_session.add(character)
        db_session.commit()
        
        try:
            export_service = ProjectExportService(db_session)
            
            # 导出项目（不包含媒体）
            zip_buffer = export_service.export_project(
                str(test_project.id),
                include_media=False
            )
            
            # 读取ZIP内容
            with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                # 验证包含characters.json
                assert "characters.json" in zip_file.namelist(), "应该包含characters.json"
                
                # 读取角色数据
                characters_json = zip_file.read("characters.json").decode('utf-8')
                characters_data = json.loads(characters_json)
                
                # 验证角色数据
                assert len(characters_data) == 1
                assert characters_data[0]["name"] == "Test Character"
                assert characters_data[0]["style"] == "anime"
        
        finally:
            # 清理
            db_session.query(Character).filter(Character.id == character.id).delete()
            db_session.commit()
    
    def test_export_project_not_found(self, db_session):
        """
        测试导出不存在的项目
        
        需求：11.6
        """
        export_service = ProjectExportService(db_session)
        
        # 尝试导出不存在的项目
        with pytest.raises(ValueError, match="项目不存在"):
            export_service.export_project("nonexistent-project-id")
    
    def test_get_export_filename(self, db_session, test_project):
        """
        测试获取导出文件名
        
        需求：11.6
        """
        export_service = ProjectExportService(db_session)
        
        # 获取文件名
        filename = export_service.get_export_filename(str(test_project.id))
        
        # 验证文件名格式
        assert filename.endswith(".zip"), "文件名应该以.zip结尾"
        assert "Test_Export_Project" in filename, "文件名应该包含项目名称"
    
    def test_export_zip_structure(self, db_session, test_project):
        """
        测试导出ZIP文件结构
        
        需求：11.6
        """
        export_service = ProjectExportService(db_session)
        
        # 导出项目
        zip_buffer = export_service.export_project(
            str(test_project.id),
            include_media=False
        )
        
        # 读取ZIP内容
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            filenames = zip_file.namelist()
            
            # 验证基本文件存在
            assert "project.json" in filenames
            assert "characters.json" in filenames
            assert "storyboard.json" in filenames
            assert "audio.json" in filenames
    
    def test_export_json_format(self, db_session, test_project):
        """
        测试导出的JSON格式正确
        
        需求：11.6
        """
        export_service = ProjectExportService(db_session)
        
        # 导出项目
        zip_buffer = export_service.export_project(
            str(test_project.id),
            include_media=False
        )
        
        # 读取ZIP内容
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            # 验证所有JSON文件格式正确
            for filename in ["project.json", "characters.json", "storyboard.json", "audio.json"]:
                json_content = zip_file.read(filename).decode('utf-8')
                
                # 尝试解析JSON
                try:
                    json.loads(json_content)
                except json.JSONDecodeError:
                    pytest.fail(f"{filename} 不是有效的JSON格式")
