# 🚀 ToonSync 部署上线指南

本指南将帮助你一步步完成 ToonSync 的部署上线。

## 📋 前提条件

- ✅ 域名：`toonsync.space`
- ✅ GitHub 账号
- ✅ Cloudflare 账号
- ✅ Supabase 账号
- ✅ PayPal 开发者账号

---

## 第一阶段：Supabase 配置（数据库 + 存储）

### 1.1 创建 Supabase 项目

1. 登录 [Supabase Dashboard](https://supabase.com/dashboard)
2. 点击 **New Project**
3. 填写项目信息：
   - **Name**: `toonsync`
   - **Database Password**: 设置一个强密码（保存好！）
   - **Region**: 选择离你用户最近的区域（如 Singapore）
4. 等待项目创建完成（约 2 分钟）

### 1.2 获取数据库连接信息

1. 进入项目后，点击 **Settings** → **Database**
2. 复制以下信息：
   - **Connection string** (URI格式)
   - 格式类似：`postgresql://postgres.xxxx:密码@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres`

### 1.3 创建存储桶

1. 点击 **Storage** → **New bucket**
2. 创建名为 `short-drama-assets` 的存储桶
3. 设置为 **Public bucket**

### 1.4 获取 API 密钥

1. 点击 **Settings** → **API**
2. 复制以下信息：
   - **Project URL**: `https://xxxx.supabase.co`
   - **anon public key**: 用于前端访问

---

## 第二阶段：Railway 配置（后端部署）

### 2.1 注册 Railway

1. 访问 [Railway](https://railway.app/)
2. 使用 GitHub 账号登录
3. 验证邮箱

### 2.2 创建新项目

1. 点击 **New Project**
2. 选择 **Deploy from GitHub repo**
3. 授权并选择你的 `toonsync` 仓库
4. Railway 会自动检测到 Python 项目

### 2.3 配置环境变量

在 Railway 项目设置中添加以下环境变量：

```bash
# 基础配置
ENVIRONMENT=production
DEBUG=False

# 数据库（从 Supabase 获取）
DATABASE_URL=postgresql://postgres.xxxx:密码@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Redis（Railway 会自动提供，或使用 Upstash）
REDIS_URL=${{Redis.REDIS_URL}}

# JWT 密钥（生成一个随机字符串）
SECRET_KEY=你的随机密钥至少32位

# CORS
ALLOWED_ORIGINS=["https://toonsync.space","https://www.toonsync.space"]

# Supabase 存储
STORAGE_TYPE=supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=你的anon_key
SUPABASE_BUCKET=short-drama-assets

# AI API 密钥
REPLICATE_API_TOKEN=r8_xxxx
ELEVENLABS_API_KEY=xxxx

# PayPal 配置
PAYPAL_CLIENT_ID=你的PayPal_Client_ID
PAYPAL_CLIENT_SECRET=你的PayPal_Client_Secret
PAYPAL_MODE=sandbox
```

### 2.4 配置域名

1. 在 Railway 项目中点击 **Settings** → **Domains**
2. 添加自定义域名：`api.toonsync.space`
3. 复制提供的 CNAME 记录

### 2.5 生成 JWT 密钥

在本地运行以下命令生成安全密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 第三阶段：Cloudflare Pages 配置（前端部署）

### 3.1 创建 Pages 项目

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 点击 **Workers & Pages** → **Create application**
3. 选择 **Pages** → **Connect to Git**
4. 授权并选择你的 GitHub 仓库
5. 配置构建设置：
   - **Framework preset**: Vite
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
   - **Root directory**: `frontend`

### 3.2 配置环境变量

在 Cloudflare Pages 设置中添加环境变量：

```bash
VITE_API_BASE_URL=https://api.toonsync.space/api/v1
VITE_WS_BASE_URL=wss://api.toonsync.space/api/v1/ws
VITE_PAYPAL_CLIENT_ID=你的PayPal_Client_ID
```

### 3.3 配置自定义域名

1. 在 Pages 项目中点击 **Custom domains**
2. 添加域名：`toonsync.space`
3. 添加域名：`www.toonsync.space`
4. Cloudflare 会自动配置 DNS

---

## 第四阶段：DNS 配置

### 4.1 在 Cloudflare DNS 中添加记录

确保你的域名 DNS 托管在 Cloudflare：

| 类型    | 名称              | 内容                          | 代理状态 |
|---------|-------------------|-------------------------------|----------|
| CNAME   | api               | Railway 提供的域名            | 已代理   |
| CNAME   | www               | toonsync.pages.dev            | 已代理   |
| CNAME   | @                 | toonsync.pages.dev            | 已代理   |

---

## 第五阶段：PayPal 配置

### 5.1 创建 PayPal 应用

1. 登录 [PayPal Developer](https://developer.paypal.com/dashboard/)
2. 点击 **My Apps & Credentials**
3. 切换到 **Live** 模式（生产环境）
4. 点击 **Create App**
5. 填写应用名称：`ToonSync`
6. 复制 **Client ID** 和 **Client Secret**

### 5.2 配置 Webhook（可选）

1. 在应用设置中添加 Webhook URL：
   - `https://api.toonsync.space/api/v1/paypal/webhook`
2. 选择要监听的事件：
   - Payment capture completed
   - Payment capture denied
   - Payment capture refunded

---

## 第六阶段：GitHub Secrets 配置

在 GitHub 仓库设置中添加以下 Secrets：

1. 进入仓库 **Settings** → **Secrets and variables** → **Actions**
2. 添加以下 Secrets：

| Secret 名称                  | 说明                              |
|------------------------------|-----------------------------------|
| RAILWAY_TOKEN                | Railway CLI Token                 |
| CLOUDFLARE_API_TOKEN         | Cloudflare API Token              |
| CLOUDFLARE_ACCOUNT_ID        | Cloudflare Account ID             |
| PAYPAL_CLIENT_ID             | PayPal Client ID                  |

### 6.1 获取 Railway Token

```bash
railway login
railway token
```

### 6.2 获取 Cloudflare API Token

1. 登录 Cloudflare Dashboard
2. 点击 **My Profile** → **API Tokens**
3. 点击 **Create Token**
4. 使用 **Edit Cloudflare Workers** 模板
5. 复制生成的 Token

---

## 第七阶段：部署验证

### 7.1 检查后端

访问以下 URL 验证后端部署：

- 健康检查：`https://api.toonsync.space/health`
- API 文档：`https://api.toonsync.space/api/docs`

### 7.2 检查前端

访问 `https://toonsync.space` 验证前端部署

### 7.3 测试完整流程

1. 注册新用户
2. 创建项目
3. 测试 AI 功能
4. 测试支付流程

---

## 🔧 常见问题

### Q: 数据库迁移失败

```bash
# 在 Railway 中手动运行迁移
railway run alembic upgrade head
```

### Q: CORS 错误

确保后端 CORS 配置包含前端域名：
```python
allowed_origins = [
    "https://toonsync.space",
    "https://www.toonsync.space",
]
```

### Q: PayPal 支付失败

1. 检查 PayPal Client ID 和 Secret 是否正确
2. 确认 PayPal 模式（sandbox/live）是否正确
3. 检查前端 PayPal SDK 加载是否成功

---

## 📊 监控与维护

### 日志查看

- **Railway**: 项目页面 → Deployments → 查看日志
- **Cloudflare Pages**: 项目页面 → Logs

### 性能监控

- 使用 Railway 内置监控
- 配置 Grafana 仪表板（可选）

---

## 🎉 部署完成！

恭喜！你的 ToonSync 应用已成功部署上线。

- 🌐 前端：https://toonsync.space
- 🔌 API：https://api.toonsync.space
- 📚 文档：https://api.toonsync.space/api/docs

如有问题，请查看日志或联系支持。
