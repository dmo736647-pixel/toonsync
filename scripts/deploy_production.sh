#!/bin/bash

# 短剧生产力工具 - 生产环境部署脚本
# 使用方法: bash scripts/deploy_production.sh

set -e

echo "========================================="
echo "短剧生产力工具 - 生产环境部署"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}错误: kubectl未安装${NC}"
    echo "请先安装kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

echo -e "${GREEN}✓ kubectl已安装${NC}"

# 检查当前context
CURRENT_CONTEXT=$(kubectl config current-context)
echo -e "${YELLOW}当前Kubernetes context: ${CURRENT_CONTEXT}${NC}"
echo ""
read -p "确认要部署到此环境吗? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "部署已取消"
    exit 0
fi

echo ""
echo "========================================="
echo "步骤1: 创建命名空间"
echo "========================================="
kubectl apply -f k8s/namespace.yaml
echo -e "${GREEN}✓ 命名空间创建完成${NC}"
echo ""

echo "========================================="
echo "步骤2: 配置Secrets"
echo "========================================="
echo -e "${YELLOW}注意: 请确保已经创建了app-secrets${NC}"
echo "如果还没有创建，请运行:"
echo "kubectl create secret generic app-secrets \\"
echo "  --from-literal=DATABASE_PASSWORD='your_password' \\"
echo "  --from-literal=SECRET_KEY='your_secret_key' \\"
echo "  --from-literal=REDIS_PASSWORD='your_redis_password' \\"
echo "  --from-literal=AWS_ACCESS_KEY_ID='your_aws_key' \\"
echo "  --from-literal=AWS_SECRET_ACCESS_KEY='your_aws_secret' \\"
echo "  -n short-drama-prod"
echo ""
read -p "Secrets已创建? (yes/no): " SECRETS_READY

if [ "$SECRETS_READY" != "yes" ]; then
    echo "请先创建Secrets，然后重新运行此脚本"
    exit 1
fi

echo ""
echo "========================================="
echo "步骤3: 应用ConfigMap"
echo "========================================="
kubectl apply -f k8s/configmap.yaml
echo -e "${GREEN}✓ ConfigMap应用完成${NC}"
echo ""

echo "========================================="
echo "步骤4: 部署PostgreSQL"
echo "========================================="
kubectl apply -f k8s/postgres-deployment.yaml
echo "等待PostgreSQL就绪..."
kubectl wait --for=condition=ready pod -l app=postgres -n short-drama-prod --timeout=300s
echo -e "${GREEN}✓ PostgreSQL部署完成${NC}"
echo ""

echo "========================================="
echo "步骤5: 部署Redis"
echo "========================================="
kubectl apply -f k8s/redis-deployment.yaml
echo "等待Redis就绪..."
kubectl wait --for=condition=ready pod -l app=redis -n short-drama-prod --timeout=300s
echo -e "${GREEN}✓ Redis部署完成${NC}"
echo ""

echo "========================================="
echo "步骤6: 运行数据库迁移"
echo "========================================="
echo -e "${YELLOW}注意: 请确保Docker镜像已构建并推送${NC}"
echo ""
read -p "Docker镜像已准备好? (yes/no): " IMAGE_READY

if [ "$IMAGE_READY" != "yes" ]; then
    echo "请先构建并推送Docker镜像，然后重新运行此脚本"
    exit 1
fi

# 这里需要替换为实际的镜像地址
# kubectl run db-migration \
#   --image=your-registry/short-drama-app:latest \
#   --restart=Never \
#   --env="DATABASE_URL=postgresql://postgres:password@postgres-service:5432/short_drama_prod" \
#   --command -- alembic upgrade head \
#   -n short-drama-prod

echo -e "${YELLOW}请手动运行数据库迁移${NC}"
echo ""

echo "========================================="
echo "步骤7: 部署应用"
echo "========================================="
kubectl apply -f k8s/app-deployment.yaml
echo "等待应用就绪..."
kubectl wait --for=condition=ready pod -l app=short-drama-app -n short-drama-prod --timeout=300s
echo -e "${GREEN}✓ 应用部署完成${NC}"
echo ""

echo "========================================="
echo "步骤8: 配置Ingress"
echo "========================================="
echo -e "${YELLOW}注意: 请确保已安装cert-manager${NC}"
kubectl apply -f k8s/ingress.yaml
echo -e "${GREEN}✓ Ingress配置完成${NC}"
echo ""

echo "========================================="
echo "步骤9: 验证部署"
echo "========================================="
echo "检查Pod状态:"
kubectl get pods -n short-drama-prod
echo ""
echo "检查服务:"
kubectl get svc -n short-drama-prod
echo ""
echo "检查Ingress:"
kubectl get ingress -n short-drama-prod
echo ""

echo "========================================="
echo "部署完成!"
echo "========================================="
echo ""
echo "下一步:"
echo "1. 检查所有Pod是否正常运行"
echo "2. 访问 https://api.yourdomain.com/health 验证健康状态"
echo "3. 访问 https://api.yourdomain.com/api/docs 查看API文档"
echo "4. 配置监控和日志系统（可选）"
echo ""
echo "监控部署:"
echo "  kubectl apply -f k8s/elasticsearch-deployment.yaml"
echo "  kubectl apply -f k8s/kibana-deployment.yaml"
echo "  kubectl apply -f k8s/filebeat-daemonset.yaml"
echo ""
echo "查看日志:"
echo "  kubectl logs -n short-drama-prod deployment/short-drama-app"
echo ""
echo "如有问题，请参考 docs/DEPLOYMENT_GUIDE.md"
echo ""
