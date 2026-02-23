"""
集成测试：认证流程
测试注册→登录→访问受保护资源的完整流程
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.conftest import test_db, client


def test_complete_auth_flow(client: TestClient, test_db):
    """测试完整的认证流程"""
    # 1. 注册新用户
    register_data = {
        "email": "integration_test@example.com",
        "password": "SecurePassword123!",
        "username": "integration_user"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == register_data["email"]
    assert user_data["username"] == register_data["username"]
    assert "id" in user_data
    user_id = user_data["id"]
    
    # 2. 登录获取token
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]
    
    # 3. 使用token访问受保护资源
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    me_data = response.json()
    assert me_data["id"] == user_id
    assert me_data["email"] == register_data["email"]
    
    # 4. 测试无效token
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=invalid_headers)
    assert response.status_code == 401
    
    # 5. 测试未提供token
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_auth_flow_with_duplicate_email(client: TestClient, test_db):
    """测试重复邮箱注册"""
    register_data = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "username": "user1"
    }
    
    # 第一次注册成功
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 200
    
    # 第二次注册失败（重复邮箱）
    register_data["username"] = "user2"
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 400


def test_auth_flow_with_wrong_password(client: TestClient, test_db):
    """测试错误密码登录"""
    # 注册用户
    register_data = {
        "email": "wrongpass@example.com",
        "password": "CorrectPassword123!",
        "username": "wrongpass_user"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 200
    
    # 使用错误密码登录
    login_data = {
        "username": register_data["email"],
        "password": "WrongPassword123!"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401


def test_auth_flow_token_expiration(client: TestClient, test_db):
    """测试token过期（模拟）"""
    # 注册并登录
    register_data = {
        "email": "expiry@example.com",
        "password": "Password123!",
        "username": "expiry_user"
    }
    
    client.post("/api/v1/auth/register", json=register_data)
    
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # 使用有效token访问
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    # 注意：实际的token过期测试需要等待或修改token过期时间
    # 这里只是验证token验证机制正常工作
