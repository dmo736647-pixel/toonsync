#!/bin/bash

# 测试运行脚本

echo "运行测试..."

# 运行所有测试
pytest

# 或者运行特定类型的测试：
# pytest -m unit          # 只运行单元测试
# pytest -m property      # 只运行属性测试
# pytest -m integration   # 只运行集成测试
# pytest -v               # 详细输出
# pytest --cov            # 生成覆盖率报告
