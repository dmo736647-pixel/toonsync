"""
部署后测试脚本

用于验证部署到云端的API是否正常工作
"""
import sys
import requests
from typing import Dict, List


class DeploymentTester:
    """部署测试器"""
    
    def __init__(self, api_url: str):
        """
        初始化测试器
        
        参数:
            api_url: API基础URL（如 https://你的项目.railway.app）
        """
        self.api_url = api_url.rstrip('/')
        self.results: List[Dict] = []
    
    def test_health_check(self) -> bool:
        """测试健康检查端点"""
        print("测试健康检查端点...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200 and response.json().get("status") == "healthy"
            self.results.append({
                "test": "健康检查",
                "success": success,
                "status_code": response.status_code,
                "response": response.json() if success else response.text
            })
            return success
        except Exception as e:
            self.results.append({
                "test": "健康检查",
                "success": False,
                "error": str(e)
            })
            return False
    
    def test_api_docs(self) -> bool:
        """测试API文档端点"""
        print("测试API文档端点...")
        try:
            response = requests.get(f"{self.api_url}/api/docs", timeout=10)
            success = response.status_code == 200
            self.results.append({
                "test": "API文档",
                "success": success,
                "status_code": response.status_code
            })
            return success
        except Exception as e:
            self.results.append({
                "test": "API文档",
                "success": False,
                "error": str(e)
            })
            return False
    
    def test_cors(self) -> bool:
        """测试CORS配置"""
        print("测试CORS配置...")
        try:
            headers = {
                "Origin": "https://example.com"
            }
            response = requests.options(f"{self.api_url}/health", headers=headers, timeout=10)
            has_cors = "access-control-allow-origin" in response.headers
            self.results.append({
                "test": "CORS配置",
                "success": has_cors,
                "headers": dict(response.headers)
            })
            return has_cors
        except Exception as e:
            self.results.append({
                "test": "CORS配置",
                "success": False,
                "error": str(e)
            })
            return False
    
    def test_register_endpoint(self) -> bool:
        """测试注册端点（不实际注册）"""
        print("测试注册端点...")
        try:
            # 发送空数据，应该返回422（验证错误）
            response = requests.post(
                f"{self.api_url}/api/v1/auth/register",
                json={},
                timeout=10
            )
            # 422表示端点存在但数据验证失败（这是预期的）
            success = response.status_code in [422, 400]
            self.results.append({
                "test": "注册端点",
                "success": success,
                "status_code": response.status_code,
                "note": "端点存在且验证正常" if success else "端点可能不存在"
            })
            return success
        except Exception as e:
            self.results.append({
                "test": "注册端点",
                "success": False,
                "error": str(e)
            })
            return False
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print(f"\n{'='*60}")
        print(f"开始测试部署: {self.api_url}")
        print(f"{'='*60}\n")
        
        tests = [
            self.test_health_check,
            self.test_api_docs,
            self.test_cors,
            self.test_register_endpoint
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            if test():
                passed += 1
                print("✅ 通过\n")
            else:
                failed += 1
                print("❌ 失败\n")
        
        # 打印总结
        print(f"\n{'='*60}")
        print(f"测试完成")
        print(f"{'='*60}")
        print(f"通过: {passed}/{len(tests)}")
        print(f"失败: {failed}/{len(tests)}")
        print(f"{'='*60}\n")
        
        # 打印详细结果
        print("详细结果：")
        for result in self.results:
            print(f"\n测试: {result['test']}")
            print(f"结果: {'✅ 通过' if result['success'] else '❌ 失败'}")
            if 'status_code' in result:
                print(f"状态码: {result['status_code']}")
            if 'error' in result:
                print(f"错误: {result['error']}")
            if 'note' in result:
                print(f"说明: {result['note']}")
        
        return failed == 0


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test_deployment.py <API_URL>")
        print("示例: python test_deployment.py https://你的项目.railway.app")
        sys.exit(1)
    
    api_url = sys.argv[1]
    tester = DeploymentTester(api_url)
    
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！部署成功！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
        sys.exit(1)


if __name__ == "__main__":
    main()
