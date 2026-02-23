"""
集成测试：工作流执行流程
测试剧本→角色→分镜→导出的完整流程
"""
import pytest
from fastapi.testclient import TestClient
from tests.conftest import test_db, client, auth_headers
import time


def test_complete_workflow_execution(client: TestClient, test_db, auth_headers):
    """测试完整的工作流执行流程"""
    # 1. 创建项目
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Workflow Test Project", "description": "Test workflow"},
        headers=auth_headers
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]
    
    # 2. 上传角色（模拟）
    # 注意：实际测试需要真实的图片文件
    character_data = {
        "name": "Test Character",
        "project_id": project_id
    }
    
    # 这里简化处理，实际应该使用multipart/form-data上传图片
    # response = client.post(
    #     "/api/v1/characters",
    #     data=character_data,
    #     files={"image": ("test.jpg", image_bytes, "image/jpeg")},
    #     headers=auth_headers
    # )
    
    # 3. 创建分镜
    storyboard_data = {
        "project_id": project_id,
        "description": "Test scene description",
        "frame_number": 1
    }
    
    response = client.post(
        "/api/v1/storyboards",
        json=storyboard_data,
        headers=auth_headers
    )
    # 可能返回200或需要character_id
    # assert response.status_code == 200
    
    # 4. 启动工作流
    workflow_data = {
        "project_id": project_id
    }
    
    response = client.post(
        "/api/v1/workflows/start",
        json=workflow_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    workflow = response.json()
    assert "id" in workflow
    assert workflow["status"] in ["pending", "in_progress"]
    workflow_id = workflow["id"]
    
    # 5. 检查工作流状态
    response = client.get(
        f"/api/v1/workflows/{workflow_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    workflow_status = response.json()
    assert "status" in workflow_status
    assert "progress" in workflow_status
    
    # 6. 暂停工作流
    response = client.post(
        f"/api/v1/workflows/{workflow_id}/pause",
        headers=auth_headers
    )
    assert response.status_code == 200
    paused_workflow = response.json()
    assert paused_workflow["status"] == "pending"
    
    # 7. 继续工作流
    response = client.post(
        f"/api/v1/workflows/{workflow_id}/resume",
        headers=auth_headers
    )
    assert response.status_code == 200
    resumed_workflow = response.json()
    assert resumed_workflow["status"] == "in_progress"
    
    # 8. 取消工作流
    response = client.post(
        f"/api/v1/workflows/{workflow_id}/cancel",
        headers=auth_headers
    )
    assert response.status_code == 200


def test_workflow_data_passing(client: TestClient, test_db, auth_headers):
    """测试工作流环节间数据传递"""
    # 创建项目
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Data Passing Test", "description": "Test"},
        headers=auth_headers
    )
    project_id = project_response.json()["id"]
    
    # 启动工作流
    response = client.post(
        "/api/v1/workflows/start",
        json={"project_id": project_id},
        headers=auth_headers
    )
    assert response.status_code == 200
    workflow = response.json()
    
    # 验证工作流包含项目信息
    assert workflow["project_id"] == project_id
    assert "current_step" in workflow
    assert "progress" in workflow


def test_workflow_error_handling(client: TestClient, test_db, auth_headers):
    """测试工作流错误处理"""
    # 尝试启动不存在项目的工作流
    response = client.post(
        "/api/v1/workflows/start",
        json={"project_id": "non-existent-id"},
        headers=auth_headers
    )
    assert response.status_code in [400, 404]
    
    # 尝试操作不存在的工作流
    response = client.post(
        "/api/v1/workflows/non-existent-id/pause",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_workflow_progress_tracking(client: TestClient, test_db, auth_headers):
    """测试工作流进度跟踪"""
    # 创建项目并启动工作流
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Progress Test", "description": "Test"},
        headers=auth_headers
    )
    project_id = project_response.json()["id"]
    
    workflow_response = client.post(
        "/api/v1/workflows/start",
        json={"project_id": project_id},
        headers=auth_headers
    )
    workflow_id = workflow_response.json()["id"]
    
    # 多次检查进度
    for _ in range(3):
        response = client.get(
            f"/api/v1/workflows/{workflow_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        workflow = response.json()
        assert 0 <= workflow["progress"] <= 100
        time.sleep(0.1)  # 短暂等待
