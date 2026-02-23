@echo off
REM Windows测试运行脚本

echo 运行测试...

REM 运行所有测试
pytest

REM 或者运行特定类型的测试：
REM pytest -m unit          # 只运行单元测试
REM pytest -m property      # 只运行属性测试
REM pytest -m integration   # 只运行集成测试
REM pytest -v               # 详细输出
REM pytest --cov            # 生成覆盖率报告
