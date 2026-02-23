# ✅ ToonSync 部署检查清单

使用此清单确保所有部署步骤都已完成。

---

## 📋 部署前准备

### 账号准备
- [ ] GitHub 账号已创建
- [ ] GitHub 仓库已创建并推送代码
- [ ] Cloudflare 账号已注册
- [ ] Supabase 账号已注册
- [ ] PayPal 开发者账号已注册
- [ ] Railway 账号已注册

### 域名准备
- [ ] 域名 `toonsync.space` 已购买
- [ ] 域名已托管在 Cloudflare
- [ ] DNS 设置已配置

### 本地环境
- [ ] Git 已安装
- [ ] Node.js 18+ 已安装
- [ ] Python 3.10+ 已安装
- [ ] 已运行 `scripts/quick_deploy.bat`

---

## 🔧 配置文件

### 环境变量
- [ ] `.env.production` 文件已创建
- [ ] `DATABASE_URL` 已配置（Supabase）
- [ ] `REDIS_URL` 已配置（Railway）
- [ ] `SECRET_KEY` 已生成并配置
- [ ] `SUPABASE_URL` 已配置
- [ ] `SUPABASE_KEY` 已配置
- [ ] `REPLICATE_API_TOKEN` 已配置
- [ ] `ELEVENLABS_API_KEY` 已配置
- [ ] `PAYPAL_CLIENT_ID` 已配置
- [ ] `PAYPAL_CLIENT_SECRET` 已配置
- [ ] `PAYPAL_MODE` 已设置（sandbox/live）

### 前端配置
- [ ] `frontend/.env.production` 已创建
- [ ] `VITE_API_BASE_URL` 已设置为 `https://api.toonsync.space/api/v1`
- [ ] `VITE_WS_BASE_URL` 已设置为 `wss://api.toonsync.space/api/v1/ws`
- [ ] `VITE_PAYPAL_CLIENT_ID` 已配置

---

## 🗄️ Supabase 配置

### 数据库
- [ ] Supabase 项目已创建
- [ ] 数据库连接字符串已复制
- [ ] 数据库迁移已运行（`alembic upgrade head`）

### 存储
- [ ] 存储桶 `short-drama-assets` 已创建
- [ ] 存储桶已设置为 Public
- [ ] 存储桶 CORS 已配置

### API
- [ ] Project URL 已复制
- [ ] anon public key 已复制

---

## 🚀 Railway 配置

### 项目设置
- [ ] Railway 项目已创建
- [ ] GitHub 仓库已连接
- [ ] 环境变量已全部配置
- [ ] 数据库迁移命令已添加到启动命令

### 域名配置
- [ ] 自定义域名 `api.toonsync.space` 已添加
- [ ] CNAME 记录已复制
- [ ] 域名 DNS 已在 Cloudflare 配置
- [ ] HTTPS 证书已自动签发

### 部署验证
- [ ] 后端部署成功
- [ ] 健康检查端点可访问：`https://api.toonsync.space/health`
- [ ] API 文档可访问：`https://api.toonsync.space/api/docs`

---

## 🌐 Cloudflare Pages 配置

### 项目设置
- [ ] Cloudflare Pages 项目已创建
- [ ] GitHub 仓库已连接
- [ ] 构建设置已配置（Vite, npm run build, dist）
- [ ] 环境变量已配置

### 域名配置
- [ ] 自定义域名 `toonsync.space` 已添加
- [ ] 自定义域名 `www.toonsync.space` 已添加
- [ ] DNS 记录已配置
- [ ] HTTPS 证书已自动签发

### 部署验证
- [ ] 前端部署成功
- [ ] 网站可访问：`https://toonsync.space`
- [ ] www 域名可访问：`https://www.toonsync.space`

---

## 💳 PayPal 配置

### 应用设置
- [ ] PayPal 开发者账号已登录
- [ ] 新应用 `ToonSync` 已创建
- [ ] Client ID 已复制
- [ ] Client Secret 已复制
- [ ] Client ID 已添加到前端环境变量
- [ ] Client Secret 已添加到后端环境变量

### Webhook（可选）
- [ ] Webhook URL 已配置：`https://api.toonsync.space/api/v1/paypal/webhook`
- [ ] Webhook 事件已选择
- [ ] Webhook 签名验证已配置

### 测试
- [ ] Sandbox 模式支付测试成功
- [ ] Live 模式支付测试成功（上线后）

---

## 🔄 GitHub Actions（可选）

### Secrets 配置
- [ ] `RAILWAY_TOKEN` 已添加到 GitHub Secrets
- [ ] `CLOUDFLARE_API_TOKEN` 已添加到 GitHub Secrets
- [ ] `CLOUDFLARE_ACCOUNT_ID` 已添加到 GitHub Secrets
- [ ] `PAYPAL_CLIENT_ID` 已添加到 GitHub Secrets

### 工作流测试
- [ ] `.github/workflows/deploy.yml` 已创建
- [ ] CI 测试通过
- [ ] 自动部署已测试

---

## ✅ 最终验证

### 功能测试
- [ ] 用户注册/登录功能正常
- [ ] 项目创建功能正常
- [ ] AI 功能正常（需要 API 密钥）
- [ ] 文件上传功能正常
- [ ] 视频导出功能正常
- [ ] PayPal 支付流程正常

### 性能测试
- [ ] 页面加载速度正常（< 3秒）
- [ ] API 响应时间正常（< 500ms）
- [ ] 数据库查询性能正常

### 安全检查
- [ ] HTTPS 已启用
- [ ] CORS 配置正确
- [ ] 敏感信息未泄露
- [ ] 环境变量已正确设置

---

## 🎉 部署完成！

所有检查项完成后，你的 ToonSync 应用已成功部署上线！

### 📊 监控清单

部署后，定期检查：

- [ ] Railway 日志正常
- [ ] Cloudflare Analytics 正常
- [ ] 数据库性能正常
- [ ] 用户反馈正常
- [ ] 支付流程正常

### 📝 维护清单

定期执行：

- [ ] 每周检查应用日志
- [ ] 每月检查 API 使用量
- [ ] 每月检查费用
- [ ] 定期备份数据库
- [ ] 更新依赖版本

---

**需要帮助？** 查看 [详细部署指南](docs/DEPLOYMENT_GUIDE_SIMPLE.md) 或提交 Issue。
