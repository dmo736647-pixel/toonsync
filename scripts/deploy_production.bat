@echo off
REM 短剧生产力工具 - 生产环境部署脚本
REM 使用方法: scripts\deploy_production.bat

echo =========================================
echo 短剧生产力工具 - 生产环境部署
echo =========================================
echo.

REM 检查kubectl
where kubectl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] kubectl未安装
    echo 请先安装kubectl: https://kubernetes.io/docs/tasks/tools/
    exit /b 1
)

echo [OK] kubectl已安装
echo.

REM 检查当前context
for /f "tokens=*" %%i in ('kubectl config current-context') do set CURRENT_CONTEXT=%%i
echo 当前Kubernetes context: %CURRENT_CONTEXT%
echo.

set /p CONFIRM="确认要部署到此环境吗? (yes/no): "
if not "%CONFIRM%"=="yes" (
    echo 部署已取消
    exit /b 0
)

echo.
echo =========================================
echo 步骤1: 创建命名空间
echo =========================================
kubectl apply -f k8s/namespace.yaml
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 命名空间创建失败
    exit /b 1
)
echo [OK] 命名空间创建完成
echo.

echo =========================================
echo 步骤2: 配置Secrets
echo =========================================
echo [注意] 请确保已经创建了app-secrets
echo 如果还没有创建，请运行:
echo kubectl create secret generic app-secrets ^
echo   --from-literal=DATABASE_PASSWORD='your_password' ^
echo   --from-literal=SECRET_KEY='your_secret_key' ^
echo   --from-literal=REDIS_PASSWORD='your_redis_password' ^
echo   --from-literal=AWS_ACCESS_KEY_ID='your_aws_key' ^
echo   --from-literal=AWS_SECRET_ACCESS_KEY='your_aws_secret' ^
echo   -n short-drama-prod
echo.

set /p SECRETS_READY="Secrets已创建? (yes/no): "
if not "%SECRETS_READY%"=="yes" (
    echo 请先创建Secrets，然后重新运行此脚本
    exit /b 1
)

echo.
echo =========================================
echo 步骤3: 应用ConfigMap
echo =========================================
kubectl apply -f k8s/configmap.yaml
if %ERRORLEVEL% NEQ 0 (
    echo [错误] ConfigMap应用失败
    exit /b 1
)
echo [OK] ConfigMap应用完成
echo.

echo =========================================
echo 步骤4: 部署PostgreSQL
echo =========================================
kubectl apply -f k8s/postgres-deployment.yaml
if %ERRORLEVEL% NEQ 0 (
    echo [错误] PostgreSQL部署失败
    exit /b 1
)
echo 等待PostgreSQL就绪...
kubectl wait --for=condition=ready pod -l app=postgres -n short-drama-prod --timeout=300s
if %ERRORLEVEL% NEQ 0 (
    echo [错误] PostgreSQL启动超时
    exit /b 1
)
echo [OK] PostgreSQL部署完成
echo.

echo =========================================
echo 步骤5: 部署Redis
echo =========================================
kubectl apply -f k8s/redis-deployment.yaml
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Redis部署失败
    exit /b 1
)
echo 等待Redis就绪...
kubectl wait --for=condition=ready pod -l app=redis -n short-drama-prod --timeout=300s
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Redis启动超时
    exit /b 1
)
echo [OK] Redis部署完成
echo.

echo =========================================
echo 步骤6: 运行数据库迁移
echo =========================================
echo [注意] 请确保Docker镜像已构建并推送
echo.

set /p IMAGE_READY="Docker镜像已准备好? (yes/no): "
if not "%IMAGE_READY%"=="yes" (
    echo 请先构建并推送Docker镜像，然后重新运行此脚本
    exit /b 1
)

echo [注意] 请手动运行数据库迁移
echo.

echo =========================================
echo 步骤7: 部署应用
echo =========================================
kubectl apply -f k8s/app-deployment.yaml
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 应用部署失败
    exit /b 1
)
echo 等待应用就绪...
kubectl wait --for=condition=ready pod -l app=short-drama-app -n short-drama-prod --timeout=300s
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 应用启动超时
    exit /b 1
)
echo [OK] 应用部署完成
echo.

echo =========================================
echo 步骤8: 配置Ingress
echo =========================================
echo [注意] 请确保已安装cert-manager
kubectl apply -f k8s/ingress.yaml
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Ingress配置失败
    exit /b 1
)
echo [OK] Ingress配置完成
echo.

echo =========================================
echo 步骤9: 验证部署
echo =========================================
echo 检查Pod状态:
kubectl get pods -n short-drama-prod
echo.
echo 检查服务:
kubectl get svc -n short-drama-prod
echo.
echo 检查Ingress:
kubectl get ingress -n short-drama-prod
echo.

echo =========================================
echo 部署完成!
echo =========================================
echo.
echo 下一步:
echo 1. 检查所有Pod是否正常运行
echo 2. 访问 https://api.yourdomain.com/health 验证健康状态
echo 3. 访问 https://api.yourdomain.com/api/docs 查看API文档
echo 4. 配置监控和日志系统（可选）
echo.
echo 监控部署:
echo   kubectl apply -f k8s/elasticsearch-deployment.yaml
echo   kubectl apply -f k8s/kibana-deployment.yaml
echo   kubectl apply -f k8s/filebeat-daemonset.yaml
echo.
echo 查看日志:
echo   kubectl logs -n short-drama-prod deployment/short-drama-app
echo.
echo 如有问题，请参考 docs/DEPLOYMENT_GUIDE.md
echo.

pause
