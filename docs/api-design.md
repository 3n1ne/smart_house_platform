# API 设计

所有后端接口使用 `/api` 前缀，返回 JSON。需要登录的接口通过 `Authorization: Bearer <token>` 传递 JWT。

## 响应格式

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

失败响应：

```json
{
  "code": 4001,
  "message": "validation error",
  "errors": {}
}
```

分页列表的 `data` 通常包含：

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total": 0
  }
}
```

## 权限边界

| 角色 | 主要权限 |
| --- | --- |
| 租客 `tenant` | 浏览房源、预约看房、查看自己的合同和账单、发起维修投诉、发送消息 |
| 房东 `landlord` | 发布和管理自己的房源、处理预约、创建合同、处理收款维修和公告 |
| 管理员 `admin` | 用户管理、全站报表、监控、公告和跨业务数据审核 |

注册接口允许创建租客和房东。管理员账号通过 `flask --app run:app seed-admin` 根据环境变量初始化。

## 路由清单

### 认证 `/api/auth`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/register` | 注册租客或房东 |
| POST | `/verification-code` | 获取登录动态验证码 |
| POST | `/login` | 登录并返回 JWT |
| GET | `/me` | 当前登录用户 |
| POST | `/logout` | 逻辑登出 |

### 用户 `/api/users`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/profile` | 当前用户资料 |
| PUT | `/profile` | 更新当前用户资料 |
| GET | `/rental-history` | 当前用户租赁历史摘要 |
| GET | `/` | 管理员用户列表 |
| PATCH | `/<user_id>/status` | 管理员修改用户状态 |

### 房源 `/api/houses`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 公开房源列表 |
| GET | `/<house_id>` | 房源详情 |
| GET | `/mine` | 房东自己的房源 |
| POST | `/` | 房东创建房源 |
| PUT | `/<house_id>` | 房东编辑房源 |
| DELETE | `/<house_id>` | 房东删除房源 |
| PATCH | `/<house_id>/status` | 房东修改房源状态 |
| POST | `/<house_id>/media` | 上传房源图片或视频 |
| DELETE | `/<house_id>/media/<media_id>` | 删除房源媒体 |

### 搜索 `/api/search`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/regions` | 城市和区域选项 |
| GET | `/layouts` | 户型选项 |
| GET | `/recommendations` | 推荐房源 |

### 预约 `/api/bookings`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/` | 租客创建看房预约 |
| GET | `/mine` | 当前用户相关预约 |
| PATCH | `/<booking_id>/status` | 房东或租客更新预约状态 |

### 合同 `/api/contracts`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/` | 房东创建合同 |
| GET | `/mine` | 当前用户相关合同 |
| PATCH | `/<contract_id>/sign` | 租客签署合同 |
| PATCH | `/<contract_id>/status` | 更新合同状态 |

### 支付 `/api/payments`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/mine` | 当前用户账单或收款 |
| PATCH | `/<payment_id>/pay` | 标记支付成功 |
| PATCH | `/<payment_id>/fail` | 标记支付失败 |
| PATCH | `/<payment_id>/refund` | 房东退款 |
| POST | `/overdue-scan` | 扫描逾期账单 |

### 消息 `/api/messages`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/conversations` | 会话列表 |
| GET | `/` | 消息列表 |
| POST | `/` | 发送消息 |
| PATCH | `/read` | 标记已读 |

### 维修和投诉

| 模块 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| `/api/repairs` | POST | `/` | 租客提交维修 |
| `/api/repairs` | GET | `/mine` | 当前用户相关维修 |
| `/api/repairs` | PATCH | `/<repair_id>/status` | 处理维修状态 |
| `/api/complaints` | POST | `/` | 租客提交投诉 |
| `/api/complaints` | GET | `/mine` | 当前用户相关投诉 |
| `/api/complaints` | PATCH | `/<complaint_id>/status` | 处理投诉状态 |

### 公告、报表和监控

| 模块 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| `/api/news` | GET | `/` | 公开公告列表 |
| `/api/news` | GET | `/mine` | 当前作者公告 |
| `/api/news` | POST | `/` | 创建公告 |
| `/api/news` | PUT | `/<news_id>` | 编辑公告 |
| `/api/news` | PATCH | `/<news_id>/status` | 发布、归档或草稿 |
| `/api/news` | DELETE | `/<news_id>` | 删除公告 |
| `/api/reports` | GET | `/overview` | 管理员报表总览 |
| `/api/monitor` | GET | `/overview` | 管理员系统监控 |

## 前端调用约定

前端默认同源访问 `/api` 和 `/uploads`。分离部署时通过 `frontend/.env` 配置：

```env
VITE_API_BASE_URL=https://example.com/api
VITE_ASSET_BASE_URL=https://example.com
```
