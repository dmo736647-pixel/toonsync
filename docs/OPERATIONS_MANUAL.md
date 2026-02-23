# 运维手册

## 概述

本手册为短剧生产力工具的运维人员提供日常运维指南，包括监控、故障处理、性能优化和应急响应。

## 目录

1. [日常运维](#日常运维)
2. [监控和告警](#监控和告警)
3. [故障处理](#故障处理)
4. [性能优化](#性能优化)
5. [安全管理](#安全管理)
6. [应急响应](#应急响应)

## 日常运维

### 每日检查清单

#### 系统健康检查

```bash
# 1. 检查所有Pod状态
kubectl get pods -n short-drama-prod

# 2. 检查服务状态
kubectl get svc -n short-drama-prod

# 3. 检查Ingress状态
kubectl get ingress -n short-drama-prod

# 4. 检查HPA状态
kubectl get hpa -n short-drama-prod

# 5. 检查PVC状态
kubectl get pvc -n short-drama-prod
```

#### 资源使用检查

```bash
# 查看Pod资源使用
kubectl top pods -n short-drama-prod

# 查看节点资源使用
kubectl top nodes

# 查看磁盘使用
kubectl exec -n short-drama-prod deployment/postgres -- df -h
```

#### 日志检查

```bash
# 检查应用错误日志
kubectl logs -n short-drama-prod deployment/short-drama-app --tail=100 | grep ERROR

# 检查数据库日志
kubectl logs -n short-drama-prod deployment/postgres --tail=50

# 检查Redis日志
kubectl logs -n short-drama-prod deployment/redis --tail=50
```

#### 备份验证

```bash
# 检查最近的备份
aws s3 ls s3://your-backup-bucket/database/ --recursive | tail -5

# 验证备份完整性
aws s3 cp s3://your-backup-bucket/database/latest.sql - | head -10
```

### 每周检查清单

#### 性能指标审查

1. 访问Grafana仪表板
2. 检查以下指标：
   - API响应时间（P95 < 2秒）
   - 错误率（< 1%）
   - 数据库连接数（< 50）
   - 缓存命中率（> 80%）
   - CPU使用率（< 70%）
   - 内存使用率（< 80%）

#### 安全审计

```bash
# 检查失败的登录尝试
kubectl logs -n short-drama-prod deployment/short-drama-app | grep "login failed" | wc -l

# 检查异常API调用
kubectl logs -n short-drama-prod deployment/short-drama-app | grep "403\|401" | tail -20

# 检查证书过期时间
kubectl get certificate -n short-drama-prod -o json | jq '.items[].status.notAfter'
```

#### 数据库维护

```bash
# 连接到数据库
kubectl exec -it -n short-drama-prod deployment/postgres -- psql -U postgres short_drama_prod

# 运行以下SQL命令：

-- 检查数据库大小
SELECT pg_size_pretty(pg_database_size('short_drama_prod'));

-- 检查表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- 检查慢查询
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- 清理过期数据（如果有）
DELETE FROM sessions WHERE expires_at < NOW() - INTERVAL '7 days';
VACUUM ANALYZE;
```

### 每月检查清单

#### 容量规划

1. 审查资源使用趋势
2. 预测未来3个月的资源需求
3. 评估是否需要扩容

#### 成本优化

1. 审查云服务账单
2. 识别未使用的资源
3. 优化存储策略

#### 灾难恢复演练

1. 测试备份恢复流程
2. 验证应急响应计划
3. 更新文档

## 监控和告警

### Prometheus指标

#### 关键指标

**应用指标**：
- `http_requests_total`: HTTP请求总数
- `http_request_duration_seconds`: 请求响应时间
- `http_requests_errors_total`: 错误请求数

**数据库指标**：
- `database_connections_active`: 活跃连接数
- `database_query_duration_seconds`: 查询时间

**缓存指标**：
- `cache_hits_total`: 缓存命中数
- `cache_misses_total`: 缓存未命中数

**AI模型指标**：
- `ai_model_requests_total`: AI模型请求数
- `ai_model_duration_seconds`: AI模型处理时间

#### 查询示例

```promql
# API错误率
rate(http_requests_errors_total[5m]) / rate(http_requests_total[5m]) * 100

# P95响应时间
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 缓存命中率
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) * 100

# 数据库连接数
database_connections_active
```

### 告警规则

#### 严重告警（立即处理）

1. **服务不可用**
   - 条件：所有Pod都不健康
   - 响应：立即检查并恢复服务

2. **API错误率过高**
   - 条件：错误率 > 10%
   - 响应：检查日志，识别问题

3. **数据库连接失败**
   - 条件：数据库连接数 = 0
   - 响应：检查数据库状态

#### 警告告警（尽快处理）

1. **API响应时间慢**
   - 条件：P95响应时间 > 5秒
   - 响应：检查性能瓶颈

2. **磁盘空间不足**
   - 条件：磁盘使用率 > 80%
   - 响应：清理或扩容

3. **内存使用率高**
   - 条件：内存使用率 > 85%
   - 响应：检查内存泄漏

### 日志分析

#### Kibana查询

**查找错误日志**：
```
level: ERROR AND kubernetes.namespace: short-drama-prod
```

**查找慢请求**：
```
response_time: >2000 AND kubernetes.namespace: short-drama-prod
```

**查找特定用户的操作**：
```
user_id: "12345" AND kubernetes.namespace: short-drama-prod
```

## 故障处理

### 常见故障场景

#### 场景1：应用Pod崩溃

**症状**：
- Pod状态为CrashLoopBackOff
- 用户无法访问服务

**诊断步骤**：
```bash
# 1. 查看Pod状态
kubectl get pods -n short-drama-prod

# 2. 查看Pod事件
kubectl describe pod <pod-name> -n short-drama-prod

# 3. 查看日志
kubectl logs <pod-name> -n short-drama-prod --previous

# 4. 检查资源限制
kubectl top pod <pod-name> -n short-drama-prod
```

**解决方案**：
1. 如果是OOM（内存不足）：增加内存限制
2. 如果是配置错误：修复ConfigMap或Secret
3. 如果是代码错误：回滚到上一个版本

```bash
# 回滚部署
kubectl rollout undo deployment/short-drama-app -n short-drama-prod

# 增加内存限制
kubectl set resources deployment/short-drama-app \
  --limits=memory=4Gi \
  -n short-drama-prod
```

#### 场景2：数据库连接池耗尽

**症状**：
- 应用日志显示"too many connections"
- API响应缓慢或超时

**诊断步骤**：
```bash
# 1. 检查数据库连接数
kubectl exec -n short-drama-prod deployment/postgres -- \
  psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 2. 查看活跃连接
kubectl exec -n short-drama-prod deployment/postgres -- \
  psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

**解决方案**：
```bash
# 1. 终止空闲连接
kubectl exec -n short-drama-prod deployment/postgres -- \
  psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '5 minutes';"

# 2. 增加最大连接数（需要重启）
kubectl exec -n short-drama-prod deployment/postgres -- \
  psql -U postgres -c "ALTER SYSTEM SET max_connections = 200;"

# 3. 重启PostgreSQL
kubectl rollout restart deployment/postgres -n short-drama-prod
```

#### 场景3：Redis内存不足

**症状**：
- Redis日志显示OOM错误
- 缓存功能失效

**诊断步骤**：
```bash
# 1. 检查Redis内存使用
kubectl exec -n short-drama-prod deployment/redis -- \
  redis-cli -a your_password INFO memory

# 2. 检查键数量
kubectl exec -n short-drama-prod deployment/redis -- \
  redis-cli -a your_password DBSIZE
```

**解决方案**：
```bash
# 1. 清理过期键
kubectl exec -n short-drama-prod deployment/redis -- \
  redis-cli -a your_password --scan --pattern "session:*" | \
  xargs kubectl exec -n short-drama-prod deployment/redis -- \
  redis-cli -a your_password DEL

# 2. 增加内存限制
kubectl set resources deployment/redis \
  --limits=memory=2Gi \
  -n short-drama-prod

# 3. 配置内存淘汰策略
kubectl exec -n short-drama-prod deployment/redis -- \
  redis-cli -a your_password CONFIG SET maxmemory-policy allkeys-lru
```

#### 场景4：磁盘空间不足

**症状**：
- Pod无法写入数据
- 日志显示"no space left on device"

**诊断步骤**：
```bash
# 1. 检查PVC使用情况
kubectl exec -n short-drama-prod deployment/postgres -- df -h

# 2. 查找大文件
kubectl exec -n short-drama-prod deployment/postgres -- \
  du -sh /var/lib/postgresql/data/* | sort -h
```

**解决方案**：
```bash
# 1. 清理旧日志
kubectl exec -n short-drama-prod deployment/postgres -- \
  find /var/lib/postgresql/data/log -name "*.log" -mtime +7 -delete

# 2. 扩展PVC（如果支持）
kubectl patch pvc postgres-pvc -n short-drama-prod \
  -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'

# 3. 清理旧备份
kubectl exec -n short-drama-prod deployment/postgres -- \
  find /backups -name "*.sql" -mtime +30 -delete
```

#### 场景5：证书过期

**症状**：
- HTTPS访问失败
- 浏览器显示证书错误

**诊断步骤**：
```bash
# 1. 检查证书状态
kubectl get certificate -n short-drama-prod

# 2. 查看证书详情
kubectl describe certificate app-tls-cert -n short-drama-prod

# 3. 检查cert-manager日志
kubectl logs -n cert-manager deployment/cert-manager
```

**解决方案**：
```bash
# 1. 删除旧证书
kubectl delete certificate app-tls-cert -n short-drama-prod

# 2. 重新创建证书
kubectl apply -f k8s/ingress.yaml

# 3. 等待证书签发
kubectl wait --for=condition=ready certificate/app-tls-cert -n short-drama-prod --timeout=300s
```

## 性能优化

### 应用层优化

#### 1. 启用缓存

```python
# 在app/core/config.py中配置
CACHE_ENABLED = True
CACHE_TTL = 300  # 5分钟

# 使用缓存装饰器
from app.core.cache import cache

@cache(ttl=300)
def get_user_projects(user_id: int):
    # 查询数据库
    pass
```

#### 2. 优化数据库查询

```python
# 使用索引
# 在模型中添加索引
class User(Base):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, index=True)

# 使用批量查询
users = db.query(User).filter(User.id.in_(user_ids)).all()

# 使用懒加载
projects = db.query(Project).options(lazyload(Project.storyboards)).all()
```

#### 3. 使用异步任务

```python
# 将耗时操作放到后台任务
from app.core.async_tasks import celery_app

@celery_app.task
def process_video_export(project_id: int):
    # 视频导出逻辑
    pass

# 在API中调用
@router.post("/export")
def export_video(project_id: int):
    process_video_export.delay(project_id)
    return {"status": "processing"}
```

### 数据库优化

#### 1. 创建索引

```sql
-- 为常用查询创建索引
CREATE INDEX idx_projects_user_created ON projects(user_id, created_at DESC);
CREATE INDEX idx_storyboards_project ON storyboards(project_id);
CREATE INDEX idx_characters_user ON characters(user_id);

-- 为全文搜索创建索引
CREATE INDEX idx_projects_name_gin ON projects USING gin(to_tsvector('english', name));
```

#### 2. 优化查询

```sql
-- 使用EXPLAIN分析查询
EXPLAIN ANALYZE
SELECT * FROM projects WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10;

-- 优化JOIN查询
-- 不好的查询
SELECT * FROM projects p
LEFT JOIN storyboards s ON p.id = s.project_id;

-- 好的查询（只选择需要的字段）
SELECT p.id, p.name, COUNT(s.id) as storyboard_count
FROM projects p
LEFT JOIN storyboards s ON p.id = s.project_id
GROUP BY p.id, p.name;
```

#### 3. 定期维护

```sql
-- 更新统计信息
ANALYZE;

-- 清理死元组
VACUUM ANALYZE;

-- 重建索引
REINDEX DATABASE short_drama_prod;
```

### Redis优化

#### 1. 使用合适的数据结构

```python
# 使用Hash存储对象
redis.hset(f"user:{user_id}", mapping={
    "name": "John",
    "email": "john@example.com"
})

# 使用Set存储唯一值
redis.sadd(f"user:{user_id}:projects", project_id)

# 使用Sorted Set存储排序数据
redis.zadd(f"leaderboard", {user_id: score})
```

#### 2. 设置过期时间

```python
# 为键设置TTL
redis.setex(f"session:{session_id}", 3600, session_data)

# 批量设置过期时间
pipe = redis.pipeline()
for key in keys:
    pipe.expire(key, 3600)
pipe.execute()
```

#### 3. 使用Pipeline

```python
# 批量操作
pipe = redis.pipeline()
for i in range(1000):
    pipe.set(f"key:{i}", f"value:{i}")
pipe.execute()
```

## 安全管理

### 访问控制

#### 1. RBAC配置

```bash
# 创建只读用户
kubectl create serviceaccount readonly-user -n short-drama-prod

# 创建角色
kubectl create role readonly \
  --verb=get,list,watch \
  --resource=pods,services,deployments \
  -n short-drama-prod

# 绑定角色
kubectl create rolebinding readonly-binding \
  --role=readonly \
  --serviceaccount=short-drama-prod:readonly-user \
  -n short-drama-prod
```

#### 2. 网络策略

```yaml
# 限制Pod间通信
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
  namespace: short-drama-prod
spec:
  podSelector:
    matchLabels:
      app: short-drama-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### 密钥管理

#### 1. 定期轮换密钥

```bash
# 更新数据库密码
NEW_PASSWORD=$(openssl rand -base64 32)

# 更新Secret
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_PASSWORD=$NEW_PASSWORD \
  --dry-run=client -o yaml | kubectl apply -f -

# 重启应用
kubectl rollout restart deployment/short-drama-app -n short-drama-prod
```

#### 2. 使用Sealed Secrets

```bash
# 安装Sealed Secrets
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# 创建Sealed Secret
echo -n "my-secret-password" | kubectl create secret generic my-secret \
  --dry-run=client --from-file=password=/dev/stdin -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

# 应用Sealed Secret
kubectl apply -f sealed-secret.yaml
```

### 审计日志

#### 1. 启用Kubernetes审计

```yaml
# audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods"]
```

#### 2. 查看审计日志

```bash
# 查看最近的审计事件
kubectl get events -n short-drama-prod --sort-by='.lastTimestamp' | tail -20

# 查看特定资源的审计日志
kubectl get events -n short-drama-prod --field-selector involvedObject.name=short-drama-app
```

## 应急响应

### 应急响应流程

#### 1. 事件分类

**P0 - 严重**：服务完全不可用
**P1 - 高**：核心功能受影响
**P2 - 中**：部分功能受影响
**P3 - 低**：性能下降

#### 2. 响应时间

- P0: 立即响应（15分钟内）
- P1: 1小时内响应
- P2: 4小时内响应
- P3: 24小时内响应

### 应急操作

#### 快速回滚

```bash
# 回滚到上一个版本
kubectl rollout undo deployment/short-drama-app -n short-drama-prod

# 回滚到特定版本
kubectl rollout undo deployment/short-drama-app --to-revision=3 -n short-drama-prod

# 查看回滚历史
kubectl rollout history deployment/short-drama-app -n short-drama-prod
```

#### 紧急扩容

```bash
# 快速增加副本数
kubectl scale deployment/short-drama-app --replicas=10 -n short-drama-prod

# 临时增加资源限制
kubectl set resources deployment/short-drama-app \
  --limits=cpu=4,memory=8Gi \
  --requests=cpu=2,memory=4Gi \
  -n short-drama-prod
```

#### 流量控制

```bash
# 限制Ingress流量
kubectl annotate ingress app-ingress \
  nginx.ingress.kubernetes.io/limit-rps=50 \
  -n short-drama-prod --overwrite

# 启用维护模式
kubectl annotate ingress app-ingress \
  nginx.ingress.kubernetes.io/default-backend=maintenance-page \
  -n short-drama-prod --overwrite
```

### 事后分析

#### 1. 收集信息

```bash
# 导出所有日志
kubectl logs -n short-drama-prod deployment/short-drama-app --since=1h > app-logs.txt

# 导出事件
kubectl get events -n short-drama-prod --sort-by='.lastTimestamp' > events.txt

# 导出配置
kubectl get all,configmap,secret,pvc,ingress -n short-drama-prod -o yaml > config-snapshot.yaml
```

#### 2. 编写事故报告

事故报告应包括：
1. 事件时间线
2. 影响范围
3. 根本原因
4. 解决方案
5. 预防措施

## 联系信息

### 团队联系方式

- **运维团队**: ops@yourdomain.com
- **开发团队**: dev@yourdomain.com
- **安全团队**: security@yourdomain.com

### 紧急联系

- **24/7热线**: +86-xxx-xxxx-xxxx
- **Slack频道**: #ops-alerts

### 升级路径

1. 一线运维 → 2. 高级运维 → 3. 运维经理 → 4. CTO

---

**文档版本**: 1.0.0  
**最后更新**: 2026年2月8日
