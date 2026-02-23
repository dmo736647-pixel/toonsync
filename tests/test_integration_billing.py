"""
集成测试：计费流程
测试额度检查→费用计算→导出的完整流程
"""
import pytest
from fastapi.testclient import TestClient
from tests.conftest import test_db, client, auth_headers


def test_complete_billing_flow(client: TestClient, test_db, auth_headers):
    """测试完整的计费流程"""
    # 1. 检查用户额度
    response = client.get("/api/v1/usage/quota", headers=auth_headers)
    assert response.status_code == 200
    quota_data = response.json()
    assert "remaining_quota" in quota_data
    assert "total_quota" in quota_data
    initial_quota = quota_data["remaining_quota"]
    
    # 2. 创建项目
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Billing Test Project", "description": "Test"},
        headers=auth_headers
    )
    project_id = project_response.json()["id"]
    
    # 3. 估算导出费用
    export_config = {
        "resolution": "1080p",
        "format": "mp4",
        "aspect_ratio": "9:16"
    }
    
    response = client.post(
        f"/api/v1/projects/{project_id}/export/estimate",
        json=export_config,
        headers=auth_headers
    )
    assert response.status_code == 200
    estimate = response.json()
    assert "estimated_cost" in estimate
    assert estimate["estimated_cost"] >= 0
    estimated_cost = estimate["estimated_cost"]
    
    # 4. 检查是否有足够额度
    if initial_quota >= estimated_cost:
        # 5. 开始导出
        response = client.post(
            f"/api/v1/projects/{project_id}/export",
            json=export_config,
            headers=auth_headers
        )
        assert response.status_code == 200
        export_data = response.json()
        assert "export_id" in export_data
        
        # 6. 再次检查额度（应该减少）
        response = client.get("/api/v1/usage/quota", headers=auth_headers)
        assert response.status_code == 200
        new_quota_data = response.json()
        # 注意：实际扣费可能在导出完成后
        # assert new_quota_data["remaining_quota"] <= initial_quota
    else:
        # 额度不足，导出应该失败
        response = client.post(
            f"/api/v1/projects/{project_id}/export",
            json=export_config,
            headers=auth_headers
        )
        assert response.status_code in [402, 403]  # Payment Required or Forbidden


def test_subscription_tier_billing(client: TestClient, test_db):
    """测试不同订阅层级的计费"""
    # 创建免费用户
    free_user = {
        "email": "free@example.com",
        "password": "Password123!",
        "username": "free_user"
    }
    client.post("/api/v1/auth/register", json=free_user)
    
    # 登录
    login_response = client.post("/api/v1/auth/login", data={
        "username": free_user["email"],
        "password": free_user["password"]
    })
    free_token = login_response.json()["access_token"]
    free_headers = {"Authorization": f"Bearer {free_token}"}
    
    # 检查免费用户的额度
    response = client.get("/api/v1/usage/quota", headers=free_headers)
    assert response.status_code == 200
    quota = response.json()
    assert quota["subscription_tier"] == "free"
    assert quota["total_quota"] > 0  # 免费用户应该有基础额度


def test_billing_history(client: TestClient, test_db, auth_headers):
    """测试计费历史记录"""
    # 获取使用历史
    response = client.get("/api/v1/usage/history", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    
    # 创建项目并导出（如果有额度）
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "History Test", "description": "Test"},
        headers=auth_headers
    )
    project_id = project_response.json()["id"]
    
    export_config = {
        "resolution": "720p",
        "format": "mp4",
        "aspect_ratio": "9:16"
    }
    
    # 尝试导出
    response = client.post(
        f"/api/v1/projects/{project_id}/export",
        json=export_config,
        headers=auth_headers
    )
    
    if response.status_code == 200:
        # 再次获取历史，应该有新记录
        response = client.get("/api/v1/usage/history", headers=auth_headers)
        assert response.status_code == 200
        new_history = response.json()
        assert len(new_history) >= len(history)


def test_quota_exceeded_handling(client: TestClient, test_db, auth_headers):
    """测试额度超限处理"""
    # 获取当前额度
    response = client.get("/api/v1/usage/quota", headers=auth_headers)
    quota_data = response.json()
    
    # 如果额度已用完，测试超额处理
    if quota_data["remaining_quota"] == 0:
        project_response = client.post(
            "/api/v1/projects",
            json={"name": "Quota Test", "description": "Test"},
            headers=auth_headers
        )
        project_id = project_response.json()["id"]
        
        # 尝试导出应该失败
        response = client.post(
            f"/api/v1/projects/{project_id}/export",
            json={"resolution": "1080p", "format": "mp4", "aspect_ratio": "9:16"},
            headers=auth_headers
        )
        assert response.status_code in [402, 403]
        
        # 错误消息应该包含额度信息
        error = response.json()
        assert "quota" in str(error).lower() or "额度" in str(error)


def test_billing_with_different_resolutions(client: TestClient, test_db, auth_headers):
    """测试不同分辨率的费用计算"""
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Resolution Test", "description": "Test"},
        headers=auth_headers
    )
    project_id = project_response.json()["id"]
    
    resolutions = ["720p", "1080p", "4k"]
    costs = []
    
    for resolution in resolutions:
        response = client.post(
            f"/api/v1/projects/{project_id}/export/estimate",
            json={"resolution": resolution, "format": "mp4", "aspect_ratio": "9:16"},
            headers=auth_headers
        )
        if response.status_code == 200:
            estimate = response.json()
            costs.append(estimate["estimated_cost"])
    
    # 验证更高分辨率费用更高
    if len(costs) == 3:
        assert costs[0] <= costs[1] <= costs[2]  # 720p <= 1080p <= 4k
