"""
快速API测试脚本
"""
import requests
import time

def test_api():
    """测试API是否正常运行"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("短剧生产力工具 - API测试")
    print("=" * 60)
    print()
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 测试1: 健康检查
    print("[测试 1/3] 健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        print()
        print("提示：请确保服务器正在运行")
        print("运行命令：start_server.bat")
        return
    
    print()
    
    # 测试2: API文档
    print("[测试 2/3] API文档...")
    try:
        response = requests.get(f"{base_url}/api/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问")
            print(f"   访问: {base_url}/api/docs")
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档访问失败: {str(e)}")
    
    print()
    
    # 测试3: 根路径
    print("[测试 3/3] 根路径...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径访问成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 根路径访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路径访问失败: {str(e)}")
    
    print()
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
    print()
    print("下一步：")
    print("1. 访问 API 文档: http://localhost:8000/api/docs")
    print("2. 测试注册接口")
    print("3. 测试登录接口")
    print()

if __name__ == "__main__":
    test_api()
