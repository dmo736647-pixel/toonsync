#!/bin/bash
# 启动监控服务脚本

echo "========================================"
echo "启动短剧生产力工具监控服务"
echo "========================================"
echo ""

echo "正在启动所有服务（包括Prometheus和Grafana）..."
docker-compose up -d

echo ""
echo "等待服务启动..."
sleep 10

echo ""
echo "========================================"
echo "服务启动完成！"
echo "========================================"
echo ""
echo "应用地址: http://localhost:8000"
echo "API文档: http://localhost:8000/api/docs"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (用户名: admin, 密码: admin)"
echo ""
echo "查看服务状态:"
docker-compose ps

echo ""
echo "查看应用日志: docker-compose logs -f app"
echo "查看Prometheus日志: docker-compose logs -f prometheus"
echo "查看Grafana日志: docker-compose logs -f grafana"
echo ""
echo "停止所有服务: docker-compose down"
echo "========================================"
