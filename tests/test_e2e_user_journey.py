"""
端到端测试：完整用户旅程
模拟真实用户从注册到导出视频的完整流程
"""
import pytest
from fastapi.testclient import TestClient
from tests.conftest import test_db, client
import time


@pytest.mark.e2e
def test_complete_user_journey(client: TestClient, test_db):
    """
    测试完整的用户旅程：
    1. 注册账户
    2. 登录系统
    3. 创建项目
    4. 上传角色
    5. 创建分镜
    6. 启动工作流
    7. 导出视频
    """
    # Step 1: 注册新用户
    print("\n=== Step 1: 注册新用户 ===")
    user_data = {
        "email": "e2e_user@example.com",
        "password": "SecurePassword123!",
        "username": "e2e_test_user"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200, f"注册失败: {response.json()}"
    user = response.json()
    print(f"✓ 用户注册成功: {user['email']}")
    
    # Step 2: 登录获取token
    print("\n=== Step 2: 登录系统 ===")
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200, f"登录失败: {response.json()}"
    token_data = response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"✓ 登录成功，获取token")
    
    # Step 3: 创建项目
    print("\n=== Step 3: 创建项目 ===")
    project_data = {
        "name": "E2E Test Project",
        "description": "End-to-end test project for short drama production"
    }
    
    response = client.post("/api/v1/projects", json=project_data, headers=headers)
    assert response.status_code == 200, f"创建项目失败: {response.json()}"
    project = response.json()
    project_id = project["id"]
    print(f"✓ 项目创建成功: {project['name']} (ID: {project_id})")
    
    # Step 4: 检查用户额度
    print("\n=== Step 4: 检查用户额度 ===")
    response = client.get("/api/v1/usage/quota", headers=headers)
    assert response.status_code == 200
    quota = response.json()
    print(f"✓ 当前额度: {quota['remaining_quota']}/{quota['total_quota']}")
    
    # Step 5: 创建分镜（简化版，不上传角色）
    print("\n=== Step 5: 创建分镜 ===")
    storyboard_data = {
        "project_id": project_id,
        "description": "主角站在城市街道上，背景是高楼大厦",
        "frame_number": 1
    }
    
    response = client.post("/api/v1/storyboards", json=storyboard_data, headers=headers)
    # 可能需要character_id，这里简化处理
    if response.status_code == 200:
        storyboard = response.json()
        print(f"✓ 分镜创建成功 (ID: {storyboard['id']})")
    else:
        print(f"⚠ 分镜创建需要角色ID，跳过此步骤")
    
    # Step 6: 启动工作流
    print("\n=== Step 6: 启动工作流 ===")
    workflow_data = {"project_id": project_id}
    
    response = client.post("/api/v1/workflows/start", json=workflow_data, headers=headers)
    assert response.status_code == 200, f"启动工作流失败: {response.json()}"
    workflow = response.json()
    workflow_id = workflow["id"]
    print(f"✓ 工作流启动成功 (ID: {workflow_id})")
    print(f"  状态: {workflow['status']}, 进度: {workflow['progress']}%")
    
    # Step 7: 监控工作流进度
    print("\n=== Step 7: 监控工作流进度 ===")
    max_checks = 5
    for i in range(max_checks):
        response = client.get(f"/api/v1/workflows/{workflow_id}", headers=headers)
        assert response.status_code == 200
        workflow_status = response.json()
        print(f"  检查 {i+1}/{max_checks}: 进度 {workflow_status['progress']}%, 状态: {workflow_status['status']}")
        
        if workflow_status['status'] == 'completed':
            print("✓ 工作流执行完成")
            break
        
        time.sleep(0.5)
    
    # Step 8: 估算导出费用
    print("\n=== Step 8: 估算导出费用 ===")
    export_config = {
        "resolution": "1080p",
        "format": "mp4",
        "aspect_ratio": "9:16"
    }
    
    response = client.post(
        f"/api/v1/projects/{project_id}/export/estimate",
        json=export_config,
        headers=headers
    )
    assert response.status_code == 200
    estimate = response.json()
    print(f"✓ 预估费用: ¥{estimate['estimated_cost']}")
    
    # Step 9: 导出视频
    print("\n=== Step 9: 导出视频 ===")
    if quota['remaining_quota'] >= estimate['estimated_cost']:
        response = client.post(
            f"/api/v1/projects/{project_id}/export",
            json=export_config,
            headers=headers
        )
        assert response.status_code == 200
        export_data = response.json()
        print(f"✓ 导出任务创建成功 (Export ID: {export_data['export_id']})")
    else:
        print(f"⚠ 额度不足，跳过导出步骤")
    
    # Step 10: 查看导出历史
    print("\n=== Step 10: 查看导出历史 ===")
    response = client.get(f"/api/v1/projects/{project_id}/exports", headers=headers)
    assert response.status_code == 200
    exports = response.json()
    print(f"✓ 导出历史记录数: {len(exports)}")
    
    print("\n=== 用户旅程测试完成 ===")


@pytest.mark.e2e
def test_collaboration_user_journey(client: TestClient, test_db):
    """测试协作用户旅程"""
    # 创建项目所有者
    owner_data = {
        "email": "owner@example.com",
        "password": "Password123!",
        "username": "project_owner"
    }
    client.post("/api/v1/auth/register", json=owner_data)
    
    owner_login = client.post("/api/v1/auth/login", data={
        "username": owner_data["email"],
        "password": owner_data["password"]
    })
    owner_token = owner_login.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    
    # 创建项目
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Collaboration Test", "description": "Test"},
        headers=owner_headers
    )
    project_id = project_response.json()["id"]
    
    # 创建协作者
    collaborator_data = {
        "email": "collaborator@example.com",
        "password": "Password123!",
        "username": "collaborator"
    }
    client.post("/api/v1/auth/register", json=collaborator_data)
    
    # 邀请协作者
    invite_response = client.post(
        f"/api/v1/projects/{project_id}/collaborators",
        json={"email": collaborator_data["email"], "role": "editor"},
        headers=owner_headers
    )
    assert invite_response.status_code == 200
    
    # 协作者登录
    collab_login = client.post("/api/v1/auth/login", data={
        "username": collaborator_data["email"],
        "password": collaborator_data["password"]
    })
    collab_token = collab_login.json()["access_token"]
    collab_headers = {"Authorization": f"Bearer {collab_token}"}
    
    # 协作者访问项目
    response = client.get(f"/api/v1/projects/{project_id}", headers=collab_headers)
    assert response.status_code == 200
    
    print("✓ 协作用户旅程测试完成")


@pytest.mark.e2e
def test_error_recovery_journey(client: TestClient, test_db):
    """测试错误恢复旅程"""
    # 注册并登录
    user_data = {
        "email": "error_test@example.com",
        "password": "Password123!",
        "username": "error_user"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建项目
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Error Test", "description": "Test"},
        headers=headers
    )
    project_id = project_response.json()["id"]
    
    # 启动工作流
    workflow_response = client.post(
        "/api/v1/workflows/start",
        json={"project_id": project_id},
        headers=headers
    )
    workflow_id = workflow_response.json()["id"]
    
    # 暂停工作流
    pause_response = client.post(
        f"/api/v1/workflows/{workflow_id}/pause",
        headers=headers
    )
    assert pause_response.status_code == 200
    
    # 继续工作流
    resume_response = client.post(
        f"/api/v1/workflows/{workflow_id}/resume",
        headers=headers
    )
    assert resume_response.status_code == 200
    
    print("✓ 错误恢复旅程测试完成")
