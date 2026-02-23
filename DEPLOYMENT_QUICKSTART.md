# 🎯 ToonSync 部署快速开始

## 📝 部署前检查清单

在开始部署之前，请确保你已完成以下准备工作：

- [ ] 已有 GitHub 账号并创建了仓库
- [ ] 已有 Cloudflare 账号（域名托管）
- [ ] 已有 Supabase 账号（数据库 + 存储）
- [ ] 已有 PayPal 开发者账号（支付）
- [ ] 已注册 Railway 账号（后端托管）
- [ ] 域名 `toonsync.space` 已在 Cloudflare 托管

---

## 🚀 5 分钟快速部署

### 第一步：运行准备脚本

```bash
# Windows
scripts\quick_deploy.bat

# Linux/Mac
chmod +x scripts/quick_deploy.sh
./scripts/quick_deploy.sh
```

这个脚本会：
1. ✅ 检查必要工具（Git, Node.js, Python）
2. ✅ 创建 `.env.production` 配置文件
3. ✅ 安装所有依赖
4. ✅ 运行数据库迁移
5. ✅ 构建前端

### 第二步：配置 Supabase（2 分钟）

1. 访问 https://supabase.com/dashboard
2. 创建新项目 `toonsync`
3. 在 **Settings → Database** 复制连接字符串
4. 在 **Storage** 创建存储桶 `short-drama-assets`
5. 在 **Settings → API** 复制 Project URL 和 anon key

### 第三步：配置 Railway（3 分钟）

1. 访问 https://railway.app/
2. 点击 **New Project** → **Deploy from GitHub**
3. 选择你的 `toonsync` 仓库
4. 在 **Variables** 中添加环境变量（从 `.env.production` 复制）
5. 添加自定义域名 `api.toonsync.space`

### 第四步：配置 Cloudflare Pages（2 分钟）

1. 访问 https://dash.cloudflare.com/
2. 点击 **Workers & Pages** → **Create application**
3. 选择 **Pages** → **Connect to Git**
4. 选择你的仓库，配置：
   - **Framework**: Vite
   - **Build command**: `npm run build`
   - **Output directory**: `dist`
   - **Root directory**: `frontend`
5. 添加自定义域名 `toonsync.space` 和 `www.toonsync.space`

### 第五步：配置 PayPal（2 分钟）

1. 访问 https://developer.paypal.com/dashboard/
2. 切换到 **Live** 模式
3. 创建新应用 `ToonSync`
4. 复制 **Client ID** 和 **Client Secret**
5. 将 Client ID 添加到 Cloudflare Pages 环境变量

---

## 🔧 配置环境变量

在 `.env.production` 文件中填入以下信息：

```bash
# 数据库（从 Supabase 获取）
DATABASE_URL=postgresql://postgres.xxxx:密码@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Redis（从 Railway 获取）
REDIS_URL=redis://default:密码@host:6379

# JWT 密钥（生成方法：python -c "import secrets; print(secrets.token_urlsafe(32))"）
SECRET_KEY=你的随机密钥

# Supabase 存储
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=你的anon_key

# AI API 密钥
REPLICATE_API_TOKEN=r8_xxxx
ELEVENLABS_API_KEY=xxxx

# PayPal
PAYPAL_CLIENT_ID=你的PayPal_Client_ID
PAYPAL_CLIENT_SECRET=你的PayPal_Client_Secret
PAYPAL_MODE=sandbox
```

---

## 🌐 DNS 配置

在 Cloudflare DNS 中添加以下记录：

| 类型    | 名称              | 内容                          | 代理   |
|---------|-------------------|-------------------------------|--------|
| CNAME   | api               | Railway 提供的域名            | ✅     |
| CNAME   | www               | toonsync.pages.dev            | ✅     |
| CNAME   | @                 | toonsync.pages.dev            | ✅     |

---

## ✅ 验证部署

部署完成后，访问以下 URL 验证：

- 🌐 前端：https://toonsync.space
- 🔌 API：https://api.toonsync.space
- 📚 文档：https://api.toonsync.space/api/docs
- ❤️ 健康检查：https://api.toonsync.space/health

---

## 🎉 完成！

你的 ToonSync 应用已成功部署上线！

### 下一步：

1. **测试功能**
   - 注册新用户
   - 创建项目
   - 测试 AI 功能
   - 测试支付流程

2. **监控应用**
   - 查看 Railway 日志
   - 查看 Cloudflare Analytics
   - 配置告警（可选）

3. **推广应用**
   - 分享到社交媒体
   - 收集用户反馈
   - 持续优化功能

---

## 📚 更多资源

- 📖 [详细部署指南](docs/DEPLOYMENT_GUIDE_SIMPLE.md)
- 🔧 [API 文档](docs/API_DOCUMENTATION.md)
- 👤 [用户手册](docs/USER_MANUAL.md)
- 🐛 [问题反馈](https://github.com/yourusername/toonsync/issues)

---

## 💡 提示

- 首次部署建议使用 PayPal **Sandbox** 模式测试
- 生产环境切换到 **Live** 模式前，确保所有测试通过
- 定期备份数据库（Supabase 提供自动备份）
- 监控 API 使用量，避免超出免费额度

---

**需要帮助？** 查看 [详细部署指南](docs/DEPLOYMENT_GUIDE_SIMPLE.md) 或提交 Issue。
