"""
负载测试：测试系统在高并发下的性能
注意：这些测试需要较长时间运行，建议单独执行
"""
import pytest
from fastapi.testclient import TestClient
from tests.conftest import test_db, client
import time
import concurrent.futures
from typing import List, Dict
import statistics


@pytest.mark.load
@pytest.mark.slow
def test_concurrent_user_registration(client: TestClient, test_db):
    """测试并发用户注册"""
    num_users = 100
    
    def register_user(index: int) -> Dict:
        user_data = {
            "email": f"load_test_user_{index}@example.com",
            "password": "Password123!",
            "username": f"load_user_{index}"
        }
        
        start_time = time.time()
        response = client.post("/api/v1/auth/register", json=user_data)
        end_time = time.time()
        
        return {
            "index": index,
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "success": response.status_code == 200
        }
    
    print(f"\n测试 {num_users} 个并发用户注册...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(register_user, range(num_users)))
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 分析结果
    success_count = sum(1 for r in results if r["success"])
    response_times = [r["response_time"] for r in results]
    
    avg_response_time = statistics.mean(response_times)
    p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
    
    print(f"\n负载测试结果:")
    print(f"  总用户数: {num_users}")
    print(f"  成功注册: {success_count} ({success_count/num_users*100:.1f}%)")
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  平均响应时间: {avg_response_time:.3f}秒")
    print(f"  P95响应时间: {p95_response_time:.3f}秒")
    print(f"  吞吐量: {num_users/total_time:.2f} 请求/秒")
    
    # 断言
    assert success_count >= num_users * 0.95, "成功率应该 >= 95%"
    assert p95_response_time < 2.0, "P95响应时间应该 < 2秒"


@pytest.mark.load
@pytest.mark.slow
def test_concurrent_api_requests(client: TestClient, test_db):
    """测试并发API请求"""
    # 先创建一个测试用户
    user_data = {
        "email": "api_load_test@example.com",
        "password": "Password123!",
        "username": "api_load_user"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建一个项目
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Load Test Project", "description": "Test"},
        headers=headers
    )
    project_id = project_response.json()["id"]
    
    num_requests = 100
    
    def make_request(index: int) -> Dict:
        start_time = time.time()
        response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
        end_time = time.time()
        
        return {
            "index": index,
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "success": response.status_code == 200
        }
    
    print(f"\n测试 {num_requests} 个并发API请求...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(make_request, range(num_requests)))
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 分析结果
    success_count = sum(1 for r in results if r["success"])
    response_times = [r["response_time"] for r in results]
    
    avg_response_time = statistics.mean(response_times)
    p95_response_time = statistics.quantiles(response_times, n=20)[18]
    
    print(f"\nAPI负载测试结果:")
    print(f"  总请求数: {num_requests}")
    print(f"  成功请求: {success_count} ({success_count/num_requests*100:.1f}%)")
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  平均响应时间: {avg_response_time:.3f}秒")
    print(f"  P95响应时间: {p95_response_time:.3f}秒")
    print(f"  吞吐量: {num_requests/total_time:.2f} 请求/秒")
    
    # 断言：95%的请求响应时间应该 < 2秒
    assert success_count == num_requests, "所有请求都应该成功"
    assert p95_response_time < 2.0, "P95响应时间应该 < 2秒"


@pytest.mark.load
@pytest.mark.slow
def test_system_availability_under_load(client: TestClient, test_db):
    """测试系统在负载下的可用性"""
    duration_seconds = 30  # 测试持续30秒
    requests_per_second = 10
    
    # 创建测试用户
    user_data = {
        "email": "availability_test@example.com",
        "password": "Password123!",
        "username": "availability_user"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    results = []
    start_time = time.time()
    request_count = 0
    
    print(f"\n测试系统可用性（持续{duration_seconds}秒，{requests_per_second}请求/秒）...")
    
    while time.time() - start_time < duration_seconds:
        # 发送请求
        try:
            response = client.get("/api/v1/projects", headers=headers)
            results.append({
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "timestamp": time.time() - start_time
            })
            request_count += 1
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e),
                "timestamp": time.time() - start_time
            })
        
        # 控制请求速率
        time.sleep(1.0 / requests_per_second)
    
    # 分析结果
    success_count = sum(1 for r in results if r["success"])
    availability = success_count / len(results) * 100
    
    print(f"\n可用性测试结果:")
    print(f"  测试时长: {duration_seconds}秒")
    print(f"  总请求数: {len(results)}")
    print(f"  成功请求: {success_count}")
    print(f"  系统可用性: {availability:.2f}%")
    
    # 断言：系统可用性应该 >= 99%
    assert availability >= 99.0, f"系统可用性应该 >= 99%，实际: {availability:.2f}%"


@pytest.mark.load
def test_response_time_percentiles(client: TestClient, test_db):
    """测试API响应时间百分位数"""
    # 创建测试用户
    user_data = {
        "email": "percentile_test@example.com",
        "password": "Password123!",
        "username": "percentile_user"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 发送多个请求并记录响应时间
    num_requests = 100
    response_times = []
    
    for _ in range(num_requests):
        start_time = time.time()
        response = client.get("/api/v1/projects", headers=headers)
        end_time = time.time()
        
        if response.status_code == 200:
            response_times.append(end_time - start_time)
    
    # 计算百分位数
    response_times.sort()
    p50 = response_times[len(response_times) // 2]
    p95 = response_times[int(len(response_times) * 0.95)]
    p99 = response_times[int(len(response_times) * 0.99)]
    
    print(f"\n响应时间百分位数:")
    print(f"  P50 (中位数): {p50:.3f}秒")
    print(f"  P95: {p95:.3f}秒")
    print(f"  P99: {p99:.3f}秒")
    
    # 断言：95%的请求响应时间应该 < 2秒
    assert p95 < 2.0, f"P95响应时间应该 < 2秒，实际: {p95:.3f}秒"
