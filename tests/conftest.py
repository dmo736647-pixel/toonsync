"""Pytest配置和fixture"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app


# 测试数据库URL
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """创建测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    session = TestingSessionLocal()
    
    # 清理所有表数据（保留表结构）
    from app.models.sound_effect import SoundEffect
    from app.models.asset import Asset
    from app.models.user import User
    from app.models.project import Project
    from app.models.character import Character
    from app.models.subscription import Subscription
    from app.models.collaboration import ProjectCollaborator, ProjectVersion, ProjectTemplate
    
    try:
        # 删除所有数据
        session.query(ProjectCollaborator).delete()
        session.query(ProjectVersion).delete()
        session.query(ProjectTemplate).delete()
        session.query(Character).delete()
        session.query(Project).delete()
        session.query(Subscription).delete()
        session.query(Asset).delete()
        session.query(SoundEffect).delete()
        session.query(User).delete()
        session.commit()
        
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data() -> dict:
    """示例用户数据"""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_project_data() -> dict:
    """示例项目数据"""
    return {
        "name": "测试项目",
        "aspect_ratio": "9:16",
        "script": "这是一个测试剧本"
    }


@pytest.fixture
def sample_character_data() -> dict:
    """示例角色数据"""
    return {
        "name": "测试角色",
        "reference_image_url": "/storage/test/character.jpg",
        "style": "anime"
    }
