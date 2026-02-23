# 前端快速启动指南

## 前提条件

- Node.js 18+ 
- npm 或 yarn

## 安装步骤

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

确保 `.env.development` 文件存在并配置正确：

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/api/v1/ws
```

### 3. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

## 功能测试

### 测试登录功能

1. 访问 http://localhost:5173/login
2. 输入邮箱和密码
3. 点击"登录"按钮
4. 成功后会跳转到项目列表页面

### 测试注册功能

1. 访问 http://localhost:5173/register
2. 输入邮箱、用户名和密码
3. 确认密码
4. 点击"注册"按钮
5. 成功后会跳转到登录页面

### 测试项目列表

1. 登录后自动跳转到 http://localhost:5173/projects
2. 查看项目列表
3. 如果没有项目，会显示空状态提示

## 常见问题

### 1. 端口被占用

如果5173端口被占用，Vite会自动使用下一个可用端口。

### 2. API连接失败

确保后端服务器正在运行：
```bash
# 在项目根目录
python -m uvicorn app.main:app --reload
```

### 3. 依赖安装失败

尝试清除缓存：
```bash
rm -rf node_modules package-lock.json
npm install
```

### 4. TypeScript错误

运行类型检查：
```bash
npm run type-check
```

## 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint

# 类型检查
npm run type-check
```

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API客户端
│   │   ├── client.ts     # Axios配置
│   │   ├── auth.ts       # 认证API
│   │   └── projects.ts   # 项目API
│   ├── components/       # 可复用组件
│   │   ├── auth/         # 认证组件
│   │   ├── feedback/     # 反馈组件
│   │   └── layout/       # 布局组件
│   ├── contexts/         # React Context
│   │   └── AuthContext.tsx
│   ├── hooks/            # 自定义Hooks
│   │   └── useWebSocket.ts
│   ├── pages/            # 页面组件
│   │   ├── Auth/         # 认证页面
│   │   └── Projects/     # 项目页面
│   ├── types/            # TypeScript类型
│   ├── App.tsx           # 根组件
│   └── main.tsx          # 入口文件
└── 配置文件
```

## 下一步

- 查看 `README.md` 了解更多详情
- 查看 `FRONTEND_IMPLEMENTATION_GUIDE.md` 了解实现指南
- 开始开发新功能

## 需要帮助？

- 查看文档：`frontend/README.md`
- 查看实现指南：`FRONTEND_IMPLEMENTATION_GUIDE.md`
- 查看完成报告：`TASK_17_COMPLETION_REPORT.md`
