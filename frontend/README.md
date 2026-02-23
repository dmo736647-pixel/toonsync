# 短剧生产力工具 - 前端

基于 React + TypeScript + Vite + TailwindCSS 构建的现代化前端应用。

## 技术栈

- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **TailwindCSS** - 样式框架
- **React Router** - 路由管理
- **Axios** - HTTP客户端

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发环境

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 生产构建

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/            # API客户端
│   │   ├── client.ts   # Axios配置
│   │   ├── auth.ts     # 认证API
│   │   └── projects.ts # 项目API
│   ├── components/     # 可复用组件
│   │   ├── auth/       # 认证组件
│   │   ├── feedback/   # 反馈组件
│   │   └── layout/     # 布局组件
│   ├── contexts/       # React Context
│   │   └── AuthContext.tsx
│   ├── hooks/          # 自定义Hooks
│   │   └── useWebSocket.ts
│   ├── pages/          # 页面组件
│   │   ├── Auth/       # 认证页面
│   │   └── Projects/   # 项目页面
│   ├── types/          # TypeScript类型
│   │   └── index.ts
│   ├── App.tsx         # 根组件
│   ├── main.tsx        # 入口文件
│   └── index.css       # 全局样式
├── .env.development    # 开发环境变量
├── .env.production     # 生产环境变量
├── index.html          # HTML模板
├── package.json        # 依赖配置
├── tsconfig.json       # TypeScript配置
├── vite.config.ts      # Vite配置
└── tailwind.config.js  # TailwindCSS配置
```

## 已实现功能

### 核心功能
- ✅ 用户认证（登录/注册）
- ✅ 项目列表和管理
- ✅ 实时反馈（WebSocket）
- ✅ 错误处理和显示
- ✅ 进度条组件
- ✅ 响应式布局

### API集成
- ✅ Axios HTTP客户端
- ✅ 请求/响应拦截器
- ✅ Token自动管理
- ✅ 错误处理

### 状态管理
- ✅ React Context API
- ✅ 认证状态管理
- ✅ 自定义Hooks

## 环境变量

### 开发环境 (.env.development)
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/api/v1/ws
```

### 生产环境 (.env.production)
```
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
VITE_WS_BASE_URL=wss://api.yourdomain.com/api/v1/ws
```

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `src/App.tsx` 添加路由
3. 如需认证，使用 `<PrivateRoute>` 包裹

### 添加新API

1. 在 `src/api/` 创建API模块
2. 使用 `apiClient` 发送请求
3. 在 `src/types/` 定义类型

### 使用WebSocket

```typescript
import { useWebSocket } from '../hooks/useWebSocket';

function MyComponent() {
  const { messages, connected, sendMessage } = useWebSocket('/feedback');
  
  // 处理消息
  useEffect(() => {
    messages.forEach(msg => {
      console.log(msg);
    });
  }, [messages]);
  
  return <div>Connected: {connected ? 'Yes' : 'No'}</div>;
}
```

## 代码规范

- 使用 TypeScript 严格模式
- 组件使用函数式组件
- 使用 Hooks 管理状态
- 遵循 React 最佳实践
- 使用 TailwindCSS 工具类

## 性能优化

- 使用 React.memo 避免不必要的重渲染
- 使用 useMemo 和 useCallback 优化计算
- 懒加载路由组件
- 图片优化和懒加载

## 浏览器支持

- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)

## 许可证

MIT
