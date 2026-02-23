# API文档

## 概述

短剧生产力工具提供RESTful API，支持用户认证、项目管理、工作流执行、视频导出等功能。

## 基本信息

- **Base URL**: `https://api.yourdomain.com/api/v1`
- **协议**: HTTPS
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### 获取访问令牌

所有API请求（除了注册和登录）都需要在请求头中包含JWT令牌：

```http
Authorization: Bearer <your_access_token>
```

### 注册

创建新用户账户。

**端点**: `POST /auth/register`

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "username": "johndoe"
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2026-02-08T10:00:00Z"
}
```

**错误响应** (400 Bad Request):
```json
{
  "detail": "Email already registered"
}
```

### 登录

使用邮箱和密码登录，获取访问令牌。

**端点**: `POST /auth/login`

**请求体** (application/x-www-form-urlencoded):
```
username=user@example.com
password=SecurePassword123!
```

**响应** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 获取当前用户信息

**端点**: `GET /auth/me`

**请求头**:
```http
Authorization: Bearer <access_token>
```

**响应** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "subscription_tier": "professional",
  "quota_remaining": 1000,
  "created_at": "2026-02-08T10:00:00Z"
}
```

## 项目管理

### 创建项目

**端点**: `POST /projects`

**请求头**:
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "我的第一个短剧",
  "description": "一个关于爱情的故事",
  "aspect_ratio": "9:16"
}
```

**响应** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "我的第一个短剧",
  "description": "一个关于爱情的故事",
  "aspect_ratio": "9:16",
  "status": "draft",
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T10:00:00Z"
}
```

### 获取项目列表

**端点**: `GET /projects`

**查询参数**:
- `skip` (int, optional): 跳过的记录数，默认0
- `limit` (int, optional): 返回的记录数，默认10
- `status` (string, optional): 过滤状态 (draft, in_progress, completed)

**请求示例**:
```http
GET /api/v1/projects?skip=0&limit=10&status=in_progress
Authorization: Bearer <access_token>
```

**响应** (200 OK):
```json
{
  "total": 25,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "我的第一个短剧",
      "description": "一个关于爱情的故事",
      "aspect_ratio": "9:16",
      "status": "in_progress",
      "created_at": "2026-02-08T10:00:00Z",
      "updated_at": "2026-02-08T10:00:00Z"
    }
  ]
}
```

### 获取项目详情

**端点**: `GET /projects/{project_id}`

**响应** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "我的第一个短剧",
  "description": "一个关于爱情的故事",
  "aspect_ratio": "9:16",
  "status": "in_progress",
  "script": "场景1：公园...",
  "characters": [
    {
      "id": 1,
      "name": "主角",
      "image_url": "https://..."
    }
  ],
  "storyboards": [
    {
      "id": 1,
      "scene_number": 1,
      "description": "主角在公园散步",
      "image_url": "https://..."
    }
  ],
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T10:00:00Z"
}
```

### 更新项目

**端点**: `PUT /projects/{project_id}`

**请求体**:
```json
{
  "name": "更新后的项目名称",
  "description": "更新后的描述",
  "script": "更新后的剧本内容"
}
```

**响应** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "更新后的项目名称",
  "description": "更新后的描述",
  "script": "更新后的剧本内容",
  "updated_at": "2026-02-08T11:00:00Z"
}
```

### 删除项目

**端点**: `DELETE /projects/{project_id}`

**响应** (200 OK):
```json
{
  "message": "Project deleted successfully"
}
```

## 角色管理

### 上传角色图片

**端点**: `POST /characters`

**请求头**:
```http
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**请求体** (multipart/form-data):
```
name: 主角
project_id: 550e8400-e29b-41d4-a716-446655440000
image: <file>
```

**响应** (200 OK):
```json
{
  "id": 1,
  "name": "主角",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "image_url": "https://storage.example.com/characters/1.jpg",
  "consistency_model_id": "model_123",
  "created_at": "2026-02-08T10:00:00Z"
}
```

### 获取角色列表

**端点**: `GET /characters`

**查询参数**:
- `project_id` (string, optional): 过滤项目ID

**响应** (200 OK):
```json
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "name": "主角",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "image_url": "https://storage.example.com/characters/1.jpg",
      "created_at": "2026-02-08T10:00:00Z"
    }
  ]
}
```

### 生成角色一致性模型

**端点**: `POST /characters/{character_id}/consistency-model`

**响应** (200 OK):
```json
{
  "character_id": 1,
  "model_id": "model_123",
  "status": "completed",
  "processing_time": 1.5,
  "created_at": "2026-02-08T10:00:00Z"
}
```

## 分镜管理

### 创建分镜

**端点**: `POST /storyboards`

**请求体**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "scene_number": 1,
  "description": "主角在公园散步，阳光明媚",
  "character_ids": [1],
  "duration": 5.0
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "scene_number": 1,
  "description": "主角在公园散步，阳光明媚",
  "image_url": null,
  "status": "pending",
  "created_at": "2026-02-08T10:00:00Z"
}
```

### 生成分镜图像

**端点**: `POST /storyboards/{storyboard_id}/generate`

**请求体**:
```json
{
  "style": "anime"
}
```

**响应** (200 OK):
```json
{
  "storyboard_id": 1,
  "image_url": "https://storage.example.com/storyboards/1.jpg",
  "status": "completed",
  "processing_time": 3.2,
  "consistency_score": 0.95
}
```

### 获取分镜列表

**端点**: `GET /storyboards`

**查询参数**:
- `project_id` (string, required): 项目ID

**响应** (200 OK):
```json
{
  "total": 10,
  "items": [
    {
      "id": 1,
      "scene_number": 1,
      "description": "主角在公园散步",
      "image_url": "https://storage.example.com/storyboards/1.jpg",
      "status": "completed",
      "duration": 5.0
    }
  ]
}
```

## 工作流管理

### 启动工作流

**端点**: `POST /workflows`

**请求体**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow_type": "full_production"
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow_type": "full_production",
  "status": "running",
  "current_step": "script_parsing",
  "progress": 0.1,
  "created_at": "2026-02-08T10:00:00Z"
}
```

### 获取工作流状态

**端点**: `GET /workflows/{workflow_id}`

**响应** (200 OK):
```json
{
  "id": 1,
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow_type": "full_production",
  "status": "running",
  "current_step": "character_generation",
  "progress": 0.4,
  "steps": [
    {
      "name": "script_parsing",
      "status": "completed",
      "started_at": "2026-02-08T10:00:00Z",
      "completed_at": "2026-02-08T10:01:00Z"
    },
    {
      "name": "character_generation",
      "status": "running",
      "started_at": "2026-02-08T10:01:00Z",
      "completed_at": null
    }
  ],
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T10:01:30Z"
}
```

### 暂停工作流

**端点**: `POST /workflows/{workflow_id}/pause`

**响应** (200 OK):
```json
{
  "id": 1,
  "status": "paused",
  "message": "Workflow paused successfully"
}
```

### 继续工作流

**端点**: `POST /workflows/{workflow_id}/resume`

**响应** (200 OK):
```json
{
  "id": 1,
  "status": "running",
  "message": "Workflow resumed successfully"
}
```

### 取消工作流

**端点**: `POST /workflows/{workflow_id}/cancel`

**响应** (200 OK):
```json
{
  "id": 1,
  "status": "cancelled",
  "message": "Workflow cancelled successfully"
}
```

## 视频导出

### 估算导出费用

**端点**: `POST /export/estimate`

**请求体**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "resolution": "1080p",
  "format": "mp4"
}
```

**响应** (200 OK):
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "estimated_cost": 50.0,
  "estimated_duration": 120,
  "video_length": 180,
  "user_quota_remaining": 1000,
  "sufficient_quota": true
}
```

### 开始导出

**端点**: `POST /export`

**请求体**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "resolution": "1080p",
  "format": "mp4",
  "include_subtitles": true
}
```

**响应** (200 OK):
```json
{
  "export_id": 1,
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 0.0,
  "estimated_completion": "2026-02-08T10:05:00Z",
  "created_at": "2026-02-08T10:00:00Z"
}
```

### 获取导出状态

**端点**: `GET /export/{export_id}`

**响应** (200 OK):
```json
{
  "export_id": 1,
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 1.0,
  "video_url": "https://storage.example.com/exports/1.mp4",
  "file_size": 52428800,
  "duration": 180,
  "resolution": "1080p",
  "format": "mp4",
  "created_at": "2026-02-08T10:00:00Z",
  "completed_at": "2026-02-08T10:03:00Z"
}
```

### 获取导出历史

**端点**: `GET /export/history`

**查询参数**:
- `skip` (int, optional): 跳过的记录数
- `limit` (int, optional): 返回的记录数

**响应** (200 OK):
```json
{
  "total": 15,
  "items": [
    {
      "export_id": 1,
      "project_name": "我的第一个短剧",
      "status": "completed",
      "video_url": "https://storage.example.com/exports/1.mp4",
      "created_at": "2026-02-08T10:00:00Z"
    }
  ]
}
```

## 订阅管理

### 获取订阅信息

**端点**: `GET /subscriptions/me`

**响应** (200 OK):
```json
{
  "user_id": 1,
  "tier": "professional",
  "status": "active",
  "quota_total": 2000,
  "quota_used": 1000,
  "quota_remaining": 1000,
  "billing_cycle": "monthly",
  "next_billing_date": "2026-03-08",
  "created_at": "2026-01-08T10:00:00Z"
}
```

### 升级订阅

**端点**: `POST /subscriptions/upgrade`

**请求体**:
```json
{
  "tier": "enterprise",
  "billing_cycle": "yearly"
}
```

**响应** (200 OK):
```json
{
  "subscription_id": 1,
  "tier": "enterprise",
  "status": "active",
  "message": "Subscription upgraded successfully"
}
```

## 计费管理

### 获取使用统计

**端点**: `GET /billing/usage`

**查询参数**:
- `start_date` (string, optional): 开始日期 (YYYY-MM-DD)
- `end_date` (string, optional): 结束日期 (YYYY-MM-DD)

**响应** (200 OK):
```json
{
  "user_id": 1,
  "period": {
    "start": "2026-02-01",
    "end": "2026-02-08"
  },
  "usage": {
    "video_exports": 10,
    "total_duration": 1800,
    "storage_used": 1073741824,
    "api_calls": 5000
  },
  "costs": {
    "video_exports": 500.0,
    "storage": 10.0,
    "total": 510.0
  }
}
```

### 获取账单历史

**端点**: `GET /billing/invoices`

**响应** (200 OK):
```json
{
  "total": 3,
  "items": [
    {
      "invoice_id": 1,
      "period": "2026-02",
      "amount": 510.0,
      "status": "paid",
      "issued_at": "2026-03-01T00:00:00Z",
      "paid_at": "2026-03-01T10:00:00Z"
    }
  ]
}
```

## 错误响应

所有API错误响应遵循统一格式：

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-02-08T10:00:00Z"
}
```

### 常见错误码

| HTTP状态码 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | BAD_REQUEST | 请求参数错误 |
| 401 | UNAUTHORIZED | 未认证或令牌无效 |
| 403 | FORBIDDEN | 权限不足 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突 |
| 422 | VALIDATION_ERROR | 数据验证失败 |
| 429 | RATE_LIMIT_EXCEEDED | 请求频率超限 |
| 500 | INTERNAL_SERVER_ERROR | 服务器内部错误 |
| 503 | SERVICE_UNAVAILABLE | 服务暂时不可用 |

## 速率限制

API实施速率限制以保护服务：

- **免费用户**: 100请求/小时
- **专业版用户**: 1000请求/小时
- **企业版用户**: 10000请求/小时

超过限制时，API返回429状态码：

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 3600
}
```

## WebSocket API

### 实时进度更新

**端点**: `wss://api.yourdomain.com/ws/progress/{workflow_id}`

**连接示例**:
```javascript
const ws = new WebSocket('wss://api.yourdomain.com/ws/progress/1?token=<access_token>');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
};
```

**消息格式**:
```json
{
  "type": "progress_update",
  "workflow_id": 1,
  "progress": 0.5,
  "current_step": "storyboard_generation",
  "message": "Generating storyboard 5/10",
  "timestamp": "2026-02-08T10:00:00Z"
}
```

## SDK和示例代码

### Python SDK

```python
from short_drama_sdk import Client

# 初始化客户端
client = Client(api_key="your_api_key")

# 创建项目
project = client.projects.create(
    name="我的短剧",
    description="一个有趣的故事"
)

# 上传角色
character = client.characters.create(
    project_id=project.id,
    name="主角",
    image_path="character.jpg"
)

# 启动工作流
workflow = client.workflows.start(
    project_id=project.id,
    workflow_type="full_production"
)

# 监控进度
for update in client.workflows.watch(workflow.id):
    print(f"Progress: {update.progress * 100}%")

# 导出视频
export = client.export.create(
    project_id=project.id,
    resolution="1080p"
)
```

### JavaScript SDK

```javascript
import { ShortDramaClient } from '@short-drama/sdk';

// 初始化客户端
const client = new ShortDramaClient({
  apiKey: 'your_api_key'
});

// 创建项目
const project = await client.projects.create({
  name: '我的短剧',
  description: '一个有趣的故事'
});

// 上传角色
const character = await client.characters.create({
  projectId: project.id,
  name: '主角',
  image: fileInput.files[0]
});

// 启动工作流
const workflow = await client.workflows.start({
  projectId: project.id,
  workflowType: 'full_production'
});

// 监控进度
client.workflows.watch(workflow.id, (update) => {
  console.log(`Progress: ${update.progress * 100}%`);
});
```

## 更多资源

- **API参考**: https://api.yourdomain.com/api/docs
- **SDK文档**: https://docs.yourdomain.com/sdk
- **示例代码**: https://github.com/yourdomain/examples
- **技术支持**: support@yourdomain.com

---

**文档版本**: 1.0.0  
**最后更新**: 2026年2月8日
