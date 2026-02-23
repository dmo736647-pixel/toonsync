# 部署指南

## 概述

本文档提供短剧生产力工具的完整部署指南，包括生产环境配置、部署流程和故障排查。

## 目录

1. [环境要求](#环境要求)
2. [准备工作](#准备工作)
3. [Kubernetes部署](#kubernetes部署)
4. [CI/CD配置](#cicd配置)
5. [监控和日志](#监控和日志)
6. [备份和恢复](#备份和恢复)
7. [故障排查](#故障排查)

## 环境要求

### 硬件要求

**最小配置**（适用于测试环境）：
- CPU: 4核
- 内存: 8GB
- 存储: 100GB SSD

**推荐配置**（适用于生产环境）：
- CPU: 16核+
- 内存: 32GB+
- 存储: 500GB+ SSD
- GPU: NVIDIA T4或更高（用于AI模型推理）

### 软件要求

- **Kubernetes**: v1.25+
- **kubectl**: v1.25+
- **Docker**: v20.10+
- **Helm**: v3.10+（可选）
- **cert-manager**: v1.10+（用于HTTPS证书）
- **NGINX Ingress Controller**: v1.5+

### 云服务要求

- **PostgreSQL**: 15+（RDS或自托管）
- **Redis**: 7+（ElastiCache或自托管）
- **S3**: 或兼容的对象存储
- **域名**: 已配置DNS解析

## 准备工作

### 1. 创建命名空间

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. 配置Secrets

**重要**: 不要在生产环境中使用示例secrets！

```bash
# 创建数据库密码
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_PASSWORD='your_strong_password' \
  --from-literal=SECRET_KEY='your_jwt_secret_key_min_32_chars' \
  --from-literal=REDIS_PASSWORD='your_redis_password' \
  --from-literal=AWS_ACCESS_KEY_ID='your_aws_key' \
  --from-literal=AWS_SECRET_ACCESS_KEY='your_aws_secret' \
  --from-literal=STRIPE_SECRET_KEY='your_stripe_key' \
  --from-literal=STRIPE_WEBHOOK_SECRET='your_webhook_secret' \
  --from-literal=SMTP_PASSWORD='your_smtp_password' \
  -n short-drama-prod
```

### 3. 配置ConfigMap

编辑 `k8s/configmap.yaml`，更新以下配置：
- `CORS_ORIGINS`: 你的前端域名
- `S3_REGION`: 你的S3区域
- `S3_BUCKET`: 你的S3桶名称

```bash
kubectl apply -f k8s/configmap.yaml
```

### 4. 配置存储类

确保你的Kubernetes集群有可用的存储类：

```bash
kubectl get storageclass
```

如果需要，创建存储类：

```bash
# 示例：AWS EBS存储类
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
EOF
```

## Kubernetes部署

### 部署顺序

按以下顺序部署组件：

#### 1. 部署PostgreSQL

```bash
kubectl apply -f k8s/postgres-deployment.yaml
```

等待PostgreSQL就绪：

```bash
kubectl wait --for=condition=ready pod -l app=postgres -n short-drama-prod --timeout=300s
```

#### 2. 部署Redis

```bash
kubectl apply -f k8s/redis-deployment.yaml
```

等待Redis就绪：

```bash
kubectl wait --for=condition=ready pod -l app=redis -n short-drama-prod --timeout=300s
```

#### 3. 初始化数据库

```bash
# 创建临时Pod运行迁移
kubectl run db-migration \
  --image=your-registry/short-drama-app:latest \
  --restart=Never \
  --env="DATABASE_URL=postgresql://postgres:password@postgres-service:5432/short_drama_prod" \
  --command -- alembic upgrade head \
  -n short-drama-prod

# 查看日志
kubectl logs db-migration -n short-drama-prod

# 清理
kubectl delete pod db-migration -n short-drama-prod
```

#### 4. 部署应用

```bash
kubectl apply -f k8s/app-deployment.yaml
```

等待应用就绪：

```bash
kubectl wait --for=condition=ready pod -l app=short-drama-app -n short-drama-prod --timeout=300s
```

#### 5. 配置Ingress

首先安装cert-manager（如果还没有）：

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

然后部署Ingress：

```bash
# 编辑ingress.yaml，更新域名
kubectl apply -f k8s/ingress.yaml
```

#### 6. 验证部署

```bash
# 检查所有Pod状态
kubectl get pods -n short-drama-prod

# 检查服务
kubectl get svc -n short-drama-prod

# 检查Ingress
kubectl get ingress -n short-drama-prod

# 测试健康检查
curl https://api.yourdomain.com/health
```

### 部署监控和日志

#### 1. 部署Elasticsearch

```bash
kubectl apply -f k8s/elasticsearch-deployment.yaml
```

#### 2. 部署Kibana

```bash
kubectl apply -f k8s/kibana-deployment.yaml
```

#### 3. 部署Filebeat

```bash
kubectl apply -f k8s/filebeat-daemonset.yaml
```

#### 4. 访问Kibana

```bash
# 获取Kibana URL
kubectl get ingress kibana-ingress -n short-drama-prod

# 访问 https://kibana.yourdomain.com
```

## CI/CD配置

### GitHub Actions配置

#### 1. 配置Secrets

在GitHub仓库设置中添加以下Secrets：

- `DOCKER_REGISTRY`: Docker镜像仓库地址
- `DOCKER_USERNAME`: Docker用户名
- `DOCKER_PASSWORD`: Docker密码
- `KUBE_CONFIG_STAGING`: Staging环境的kubeconfig（Base64编码）
- `KUBE_CONFIG_PROD`: Production环境的kubeconfig（Base64编码）

#### 2. 获取kubeconfig

```bash
# 获取kubeconfig
kubectl config view --raw > kubeconfig.yaml

# Base64编码
cat kubeconfig.yaml | base64 -w 0
```

将输出的Base64字符串添加到GitHub Secrets。

#### 3. 触发部署

**自动部署**：
- 推送到 `main` 分支 → 自动部署到Staging
- 创建 `v*` 标签 → 自动部署到Production

**手动部署**：
```bash
# 在GitHub Actions页面选择"CD - 持续部署"工作流
# 点击"Run workflow"，选择环境
```

### 部署流程

1. **代码推送** → 触发CI流程
2. **CI流程**：
   - 代码检查（Lint）
   - 运行测试
   - 安全扫描
   - 构建Docker镜像
3. **CD流程**：
   - 部署到Kubernetes
   - 运行数据库迁移
   - 健康检查
   - E2E测试
4. **部署成功** → 发送通知

## 监控和日志

### Prometheus监控

访问Prometheus：
```bash
kubectl port-forward -n short-drama-prod svc/prometheus 9090:9090
```

打开浏览器：http://localhost:9090

### Grafana仪表板

访问Grafana：
```bash
kubectl port-forward -n short-drama-prod svc/grafana 3000:3000
```

打开浏览器：http://localhost:3000
- 用户名：admin
- 密码：admin

### Kibana日志

访问Kibana：https://kibana.yourdomain.com

创建索引模式：
1. 进入 Management → Index Patterns
2. 创建索引模式：`filebeat-short-drama-*`
3. 选择时间字段：`@timestamp`

### 告警配置

编辑 `alert_rules.yml` 配置告警规则，然后重启Prometheus：

```bash
kubectl rollout restart deployment/prometheus -n short-drama-prod
```

## 备份和恢复

### 数据库备份

#### 自动备份

系统每24小时自动备份一次，保留90天。

#### 手动备份

```bash
# 备份数据库
kubectl exec -n short-drama-prod deployment/postgres -- \
  pg_dump -U postgres short_drama_prod > backup-$(date +%Y%m%d).sql

# 上传到S3
aws s3 cp backup-$(date +%Y%m%d).sql s3://your-backup-bucket/database/
```

### 数据库恢复

```bash
# 从S3下载备份
aws s3 cp s3://your-backup-bucket/database/backup-20260208.sql .

# 恢复数据库
kubectl exec -i -n short-drama-prod deployment/postgres -- \
  psql -U postgres short_drama_prod < backup-20260208.sql
```

### 应用配置备份

```bash
# 备份所有配置
kubectl get all,configmap,secret,pvc,ingress -n short-drama-prod -o yaml > backup-config.yaml

# 恢复配置
kubectl apply -f backup-config.yaml
```

## 扩缩容

### 手动扩缩容

```bash
# 扩展应用副本数
kubectl scale deployment/short-drama-app --replicas=5 -n short-drama-prod

# 查看状态
kubectl get pods -n short-drama-prod -l app=short-drama-app
```

### 自动扩缩容

HPA（Horizontal Pod Autoscaler）已配置，会根据CPU和内存使用率自动扩缩容：
- 最小副本数：3
- 最大副本数：10
- CPU目标：70%
- 内存目标：80%

查看HPA状态：

```bash
kubectl get hpa -n short-drama-prod
```

## 故障排查

### 常见问题

#### 1. Pod无法启动

```bash
# 查看Pod状态
kubectl get pods -n short-drama-prod

# 查看Pod详情
kubectl describe pod <pod-name> -n short-drama-prod

# 查看Pod日志
kubectl logs <pod-name> -n short-drama-prod

# 查看前一个容器的日志（如果容器重启了）
kubectl logs <pod-name> -n short-drama-prod --previous
```

#### 2. 数据库连接失败

```bash
# 测试数据库连接
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -n short-drama-prod -- \
  psql -h postgres-service -U postgres -d short_drama_prod

# 检查数据库Pod
kubectl logs -n short-drama-prod deployment/postgres
```

#### 3. Redis连接失败

```bash
# 测试Redis连接
kubectl run -it --rm debug --image=redis:7-alpine --restart=Never -n short-drama-prod -- \
  redis-cli -h redis-service -a your_password ping

# 检查Redis Pod
kubectl logs -n short-drama-prod deployment/redis
```

#### 4. Ingress无法访问

```bash
# 检查Ingress状态
kubectl describe ingress app-ingress -n short-drama-prod

# 检查Ingress Controller日志
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# 检查证书状态
kubectl get certificate -n short-drama-prod
kubectl describe certificate app-tls-cert -n short-drama-prod
```

#### 5. 应用性能问题

```bash
# 查看资源使用情况
kubectl top pods -n short-drama-prod

# 查看HPA状态
kubectl get hpa -n short-drama-prod

# 查看应用日志
kubectl logs -n short-drama-prod deployment/short-drama-app --tail=100
```

### 调试技巧

#### 进入容器调试

```bash
# 进入应用容器
kubectl exec -it -n short-drama-prod deployment/short-drama-app -- /bin/bash

# 进入数据库容器
kubectl exec -it -n short-drama-prod deployment/postgres -- /bin/bash
```

#### 查看事件

```bash
# 查看命名空间事件
kubectl get events -n short-drama-prod --sort-by='.lastTimestamp'
```

#### 网络调试

```bash
# 创建调试Pod
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -n short-drama-prod -- /bin/bash

# 在调试Pod中测试连接
curl http://app-service
curl http://postgres-service:5432
```

## 安全最佳实践

### 1. Secrets管理

- 使用Sealed Secrets或External Secrets Operator
- 定期轮换密钥
- 使用云提供商的密钥管理服务

### 2. 网络策略

```bash
# 应用网络策略限制Pod间通信
kubectl apply -f k8s/network-policies.yaml
```

### 3. RBAC配置

- 最小权限原则
- 定期审计权限
- 使用ServiceAccount

### 4. 镜像安全

- 使用官方镜像
- 定期扫描漏洞
- 使用镜像签名

### 5. 数据加密

- 启用数据库加密
- 使用HTTPS/TLS
- 加密敏感数据

## 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_project_user ON projects(user_id);

-- 配置连接池
-- 在app配置中设置：
-- SQLALCHEMY_POOL_SIZE=20
-- SQLALCHEMY_MAX_OVERFLOW=10
```

### 2. Redis优化

```bash
# 配置Redis持久化
# 在redis配置中：
# appendonly yes
# appendfsync everysec
```

### 3. 应用优化

- 启用缓存
- 使用异步任务
- 优化数据库查询
- 使用CDN加速静态资源

## 维护计划

### 日常维护

- 监控系统指标
- 检查日志错误
- 验证备份完整性

### 每周维护

- 审查性能指标
- 检查磁盘使用
- 更新安全补丁

### 每月维护

- 数据库优化
- 清理旧日志
- 审计安全配置

## 联系支持

如有问题，请联系：
- 技术支持：support@yourdomain.com
- 紧急热线：+86-xxx-xxxx-xxxx

## 附录

### A. 环境变量清单

参考 `k8s/configmap.yaml` 和 `k8s/secrets.yaml`

### B. 端口清单

- 8000: 应用HTTP端口
- 9090: Prometheus指标端口
- 5432: PostgreSQL端口
- 6379: Redis端口
- 9200: Elasticsearch端口
- 5601: Kibana端口

### C. 资源配额

参考各deployment文件中的resources配置

---

**文档版本**: 1.0.0  
**最后更新**: 2026年2月8日
