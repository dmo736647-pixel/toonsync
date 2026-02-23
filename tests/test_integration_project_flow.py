"""
集成测试：项目管理流程
测试创建→编辑→删除的完整流程
"""
import pytest
from fastapi.testclient import TestClient
from tests.conftest import test_db, client, auth_headers


def test_complete_project_flow(client: TestClient, test_db, auth_headers):
    """测试完整的项目管理流程"""
    # 1. 创建项目
    project_data = {
        "name": "Integration Test Project",
        "description": "A project for integration testing"
    }
    
    response = client.post(
        "/api/v1/projects",
        json=project_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    project = response.json()
    assert project["name"] == project_data["name"]
    assert project["description"] == project_data["description"]
    assert "id" in project
    project_id = project["id"]
    
    # 2. 获取项目列表
    response = client.get("/api/v1/projects", headers=auth_headers)
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= 1
    assert any(p["id"] == project_id for p in projects)
    
    # 3. 获取单个项目
    response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    fetched_project = response.json()
    assert fetched_project["id"] == project_id
    assert fetched_project["name"] == project_data["name"]
    
    # 4. 更新项目
    update_data = {
        "name": "Updated Project Name",
        "description": "Updated description"
    }
    
    response = client.put(
        f"/api/v1/projects/{project_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["name"] == update_data["name"]
    assert updated_project["description"] == update_data["description"]
    
    # 5. 删除项目
    response = client.delete(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # 6. 验证项目已删除
    response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 404


def test_project_access_control(client: TestClient, test_db):
    """测试项目访问控制"""
    # 创建两个用户
    user1_data = {
        "email": "user1@example.com",
        "password": "Password123!",
        "username": "user1"
    }
    user2_data = {
        "email": "user2@example.com",
        "password": "Password123!",
        "username": "user2"
    }
    
    client.post("/api/v1/auth/register", json=user1_data)
    client.post("/api/v1/auth/register", json=user2_data)
    
    # 用户1登录并创建项目
    login_response = client.post("/api/v1/auth/login", data={
        "username": user1_data["email"],
        "password": user1_data["password"]
    })
    user1_token = login_response.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "User1 Project", "description": "Test"},
        headers=user1_headers
    )
    project_id = project_response.json()["id"]
    
    # 用户2登录
    login_response = client.post("/api/v1/auth/login", data={
        "username": user2_data["email"],
        "password": user2_data["password"]
    })
    user2_token = login_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    
    # 用户2尝试访问用户1的项目（应该失败或只能看到自己的项目）
    response = client.get("/api/v1/projects", headers=user2_headers)
    assert response.status_code == 200
    user2_projects = response.json()
    # 用户2不应该看到用户1的项目
    assert not any(p["id"] == project_id for p in user2_projects)


def test_project_collaboration_flow(client: TestClient, test_db, auth_headers):
    """测试项目协作流程"""
    # 1. 创建项目
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Collaboration Project", "description": "Test collaboration"},
        headers=auth_headers
    )
    project_id = project_response.json()["id"]
    
    # 2. 创建第二个用户
    collaborator_data = {
        "email": "collaborator@example.com",
        "password": "Password123!",
        "username": "collaborator"
    }
    client.post("/api/v1/auth/register", json=collaborator_data)
    
    # 3. 邀请协作者
    invite_data = {
        "email": collaborator_data["email"],
        "role": "editor"
    }
    
    response = client.post(
        f"/api/v1/projects/{project_id}/collaborators",
        json=invite_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # 4. 获取协作者列表
    response = client.get(
        f"/api/v1/projects/{project_id}/collaborators",
        headers=auth_headers
    )
    assert response.status_code == 200
    collaborators = response.json()
    assert len(collaborators) >= 1
    assert any(c["email"] == collaborator_data["email"] for c in collaborators)
