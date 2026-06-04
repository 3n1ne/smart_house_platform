# API 设计

## 设计范围

本文档定义智能租赁系统的第一轮 REST API 契约。重点涵盖将首先实现的模块：

1. 认证
2. 用户个人资料
3. 房源管理
4. 搜索与房源展示
5. 预约
6. 合同
7. 支付
8. 消息
9. 维修
10. 投诉
11. 报表
12. 监控
13. 新闻

## 通用规则

### 基础路径

所有 API 使用 `/api` 前缀。

### 响应格式

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
  "errors": {
    "field": ["error detail"]
  }
}
```

### 认证

1. 使用 JWT 进行需要认证的请求。
2. 客户端通过 `Authorization: Bearer <token>` 发送令牌。
3. 基于角色的权限控制对房东、租客和管理员路由分别强制执行。

### 分页约定

列表 API 接收：

| 字段 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| page | int | 1 | 当前页码 |
| page_size | int | 10 | 每页大小 |

分页响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 0
    }
  }
}
```

## 认证模块

### `POST /api/auth/register`

注册新用户账户。

初始注册允许的角色：`landlord`、`tenant`

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| role | string | 是 | `landlord` 或 `tenant` |
| username | string | 是 | 唯一用户名 |
| password | string | 是 | 哈希前的明文密码 |
| email | string | 否 | 邮箱 |
| phone | string | 否 | 手机号 |
| real_name | string | 否 | 真实姓名 |
| identity_no | string | 否 | 身份证号，后端加密存储且响应只返回脱敏值 |
| enable_mfa | bool | 否 | 是否启用动态验证码登录 |

响应数据：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| user_id | int | 创建的用户 ID |
| username | string | 用户名 |
| role | string | 用户角色 |

### `POST /api/auth/verification-code`

为登录生成动态验证码。

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| username | string | 是 | 用户名、手机号或邮箱 |

响应数据：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| expires_in | int | 验证码有效秒数 |
| expires_at | string | 验证码过期时间，用户存在且可用时返回 |
| delivery | string | `response` 或配置的发送渠道 |
| verification_code | string | 开发/测试环境可见；生产默认不返回 |

### `POST /api/auth/login`

认证用户并返回 JWT。

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| username | string | 是 | 用户名、手机号或邮箱 |
| password | string | 是 | 明文密码 |
| verification_code | string | 否 | 开启双因素或全局 MFA 时必填 |

响应数据：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| access_token | string | JWT 访问令牌 |
| token_type | string | 通常为 `Bearer` |
| user | object | 用户基本信息 |

### `GET /api/auth/me`

返回当前已认证用户信息。

权限：已认证用户

### `POST /api/auth/logout`

当前阶段将其保留为逻辑登出端点，用于前端集成。令牌黑名单可在以后添加。

权限：已认证用户

## 用户模块

### `GET /api/users/profile`

获取当前用户个人资料。

权限：已认证用户

响应字段：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | int | 用户 ID |
| username | string | 用户名 |
| role | string | 角色编码 |
| email | string | 邮箱 |
| phone | string | 手机号 |
| real_name | string | 真实姓名 |
| avatar_url | string | 头像 URL |
| status | string | 用户状态 |
| identity_no_masked | string | 脱敏身份证号 |
| is_mfa_enabled | bool | 是否启用动态验证码登录 |

### `PUT /api/users/profile`

更新当前用户个人资料。

权限：已认证用户

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| real_name | string | 否 | 真实姓名 |
| email | string | 否 | 邮箱 |
| phone | string | 否 | 手机号 |
| avatar_url | string | 否 | 头像 URL |
| gender | string | 否 | 性别 |
| identity_no | string | 否 | 身份证号，后端加密存储且响应只返回脱敏值 |
| is_mfa_enabled | bool | 否 | 是否启用动态验证码登录 |

### `GET /api/users/rental-history`

获取当前用户的租赁历史摘要。

权限：已认证用户

行为：

1. 租客返回自己相关的预约、合同、账单、维修和投诉。
2. 房东返回自己房源相关的预约、合同、收款、维修和投诉。
3. 管理员返回全站最近记录和总数。

响应数据：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| summary | object | 各类记录总数 |
| recent_bookings | array | 最近预约记录 |
| recent_contracts | array | 最近合同记录 |
| recent_payments | array | 最近支付记录 |
| recent_repairs | array | 最近维修记录 |
| recent_complaints | array | 最近投诉记录 |

### `GET /api/users`

获取用户列表。

权限：仅管理员

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| role | string | 否 | 按角色筛选 |
| status | string | 否 | 按状态筛选 |
| keyword | string | 否 | 用户名、真实姓名、手机号 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `PATCH /api/users/{user_id}/status`

更新用户状态。

权限：仅管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 是 | `active` 或 `disabled` |

前端管理员仪表盘现在使用这些 API 进行角色/状态/关键词筛选以及账户启用/禁用操作。

## 房源模块

### `POST /api/houses`

创建新房源信息。

权限：仅房东

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| title | string | 是 | 房源标题 |
| province | string | 否 | 省份 |
| city | string | 是 | 城市 |
| district | string | 是 | 区域 |
| community | string | 否 | 小区 |
| address_detail | string | 是 | 详细地址 |
| house_type | string | 否 | 房屋类型 |
| layout | string | 是 | 户型 |
| area | number | 是 | 面积 |
| rent | number | 是 | 月租金 |
| deposit | number | 否 | 押金 |
| decoration | string | 否 | 装修情况 |
| floor | int | 否 | 楼层 |
| total_floors | int | 否 | 总楼层 |
| orientation | string | 否 | 朝向 |
| description | string | 否 | 描述 |

### `GET /api/houses`

获取公开房源列表。

权限：公开

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| city | string | 否 | 城市筛选 |
| district | string | 否 | 区域筛选 |
| layout | string | 否 | 户型筛选 |
| min_rent | number | 否 | 最低租金 |
| max_rent | number | 否 | 最高租金 |
| status | string | 否 | 公开列表默认为 `available` |
| keyword | string | 否 | 搜索标题或地址 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

响应条目字段：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | int | 房源 ID |
| title | string | 房源标题 |
| city | string | 城市 |
| district | string | 区域 |
| layout | string | 户型 |
| area | number | 面积 |
| rent | number | 月租金 |
| status | string | 房源状态 |
| cover_url | string | 封面图片 URL |

### `GET /api/houses/mine`

获取当前房东管理的房源列表。

权限：房东或管理员

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 否 | 按房源状态筛选 |
| city | string | 否 | 按城市筛选 |
| keyword | string | 否 | 搜索标题、小区或地址 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `GET /api/houses/{house_id}`

获取房源详情。

权限：公开

### `PUT /api/houses/{house_id}`

更新房源信息。

权限：仅房源所属房东

### `DELETE /api/houses/{house_id}`

删除或逻辑下架房源信息。

权限：房源所属房东或管理员

### `PATCH /api/houses/{house_id}/status`

更新房源状态。

权限：房源所属房东或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 是 | `draft`、`available`、`rented`、`repairing`、`offline` |

### `POST /api/houses/{house_id}/media`

上传房源媒体。支持 multipart 文件上传和外部媒体 URL 元数据。

权限：仅房源所属房东

外部媒体的 JSON 请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| media_type | string | 是 | `image` 或 `video` |
| file_url | string | 是 | 上传文件 URL |
| sort_order | int | 否 | 排序顺序 |

本地上传的 Multipart 表单数据：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| file | file | 是 | 图片或视频文件 |
| sort_order | int | 否 | 排序顺序 |

上传的文件通过 `/uploads/<path>` 提供访问。

### `DELETE /api/houses/{house_id}/media/{media_id}`

删除房源媒体记录。如果媒体文件存储在本地上传文件夹中，文件也会被一并删除。

权限：房源所属房东或管理员

## 搜索模块

### `GET /api/search/regions`

按区域聚合房源。

权限：公开

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| city | string | 否 | 城市筛选 |
| district | string | 否 | 区域筛选 |
| layout | string | 否 | 户型筛选 |
| keyword | string | 否 | 标题、城市、区域、小区、地址或户型关键词 |

响应条目字段：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| city | string | 城市 |
| district | string | 区域 |
| community | string | 小区 |
| house_count | int | 匹配房源数量 |
| min_rent | number | 当前聚合内最低月租 |
| max_rent | number | 当前聚合内最高月租 |

### `GET /api/search/layouts`

按户型聚合房源。

权限：公开

查询参数同 `/api/search/regions`。

响应条目字段：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| layout | string | 房源户型 |
| house_count | int | 匹配房源数量 |
| min_rent | number | 当前户型最低月租 |
| max_rent | number | 当前户型最高月租 |

### `GET /api/search/recommendations`

返回推荐房源。当前阶段可使用基于规则的推荐，如最新房源或相似价格区间的房源。

权限：公开

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| house_id | int | 否 | 作为相似推荐基准的房源 |
| city | string | 否 | 城市筛选 |
| limit | int | 否 | 返回结果数量 |

推荐规则：

1. 提供 `house_id` 时，优先返回同城、同区、同户型或租金在基准房源上下 20% 区间内的可租房源。
2. 相似房源不足时，回退返回最新发布的其他可租房源。
3. 未提供 `house_id` 时，可按 `city` 返回该城市最新可租房源；未提供 `city` 时返回全站最新可租房源。

## 预约模块

### `POST /api/bookings`

创建新的看房预约。

权限：仅租客

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| house_id | int | 是 | 目标房源 ID |
| appointment_time | string | 是 | ISO 日期时间字符串 |
| remark | string | 否 | 预约备注 |

### `GET /api/bookings/mine`

获取当前用户的预约记录。

权限：租客、房东或管理员

行为：

1. 租客获取自己创建的预约。
2. 房东获取自己房源的预约。
3. 管理员获取所有预约。

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 否 | 按预约状态筛选 |
| house_id | int | 否 | 按房源筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `PATCH /api/bookings/{booking_id}/status`

更新预约状态。

权限：

1. 房源所属房东或管理员可设置为 `confirmed`、`cancelled`、`completed`。
2. 租客只能将自己的预约设置为 `cancelled`。

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 是 | `confirmed`、`cancelled` 或 `completed` |

## 合同模块

### `POST /api/contracts`

从符合条件的预约创建租赁合同。

权限：房东或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| booking_id | int | 是 | 已确认或已完成的预约 ID |
| start_date | string | 是 | 租赁开始日期，格式 `YYYY-MM-DD` |
| end_date | string | 是 | 租赁结束日期，格式 `YYYY-MM-DD` |
| payment_cycle | string | 否 | 默认为 `monthly` |
| content | string | 否 | 合同内容 |

### `GET /api/contracts/mine`

获取与当前用户相关的合同。

权限：租客、房东或管理员

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 否 | 按合同状态筛选 |
| house_id | int | 否 | 按房源筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `PATCH /api/contracts/{contract_id}/sign`

租客签署已准备好的合同。

权限：租客或管理员

行为：

1. 合同必须处于 `draft` 状态。
2. 成功后，合同变为 `active`。
3. 自动生成初始待支付款项。

### `PATCH /api/contracts/{contract_id}/status`

更新合同生命周期状态。

权限：房源所属房东或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 是 | `terminated` 或 `expired` |

## 支付模块

### `GET /api/payments/mine`

获取与当前用户相关的支付记录。

权限：租客、房东或管理员

行为：

1. 租客获取当前用户作为付款方的支付记录。
2. 房东获取当前用户作为收款方的支付记录。
3. 管理员获取所有支付记录。

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 否 | 按支付状态筛选 |
| contract_id | int | 否 | 按合同筛选 |
| payment_type | string | 否 | 按支付类型筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `PATCH /api/payments/{payment_id}/pay`

将支付标记为已支付。

权限：付款方或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| payment_method | string | 是 | 如 `bank`、`alipay` 或 `wechat` |
| transaction_no | string | 否 | 可选交易参考号 |

行为：

1. 只允许付款方租客或管理员处理待支付/逾期账单。
2. 未传入 `transaction_no` 时，后端生成模拟交易流水号，用于开发阶段闭环。

### `PATCH /api/payments/{payment_id}/fail`

将待支付或逾期支付标记为失败。

权限：付款方租客或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| payment_method | string | 否 | 失败支付方式 |
| reason | string | 否 | 失败原因 |

### `PATCH /api/payments/{payment_id}/refund`

将已支付账单登记为已退款。

权限：收款方房东或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| reason | string | 否 | 退款原因 |

### `POST /api/payments/overdue-scan`

扫描并标记已过期的待支付账单。

权限：房东或管理员

行为：

1. 房东只扫描自己作为收款方的账单。
2. 管理员扫描所有账单。
3. `due_date` 早于当前日期且状态为 `pending` 的账单会更新为 `overdue`。

## 消息模块

### `GET /api/messages/conversations`

获取当前用户的会话摘要列表。

权限：已认证用户

响应数据：

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| conversation_key | string | 由房源和对方组成的会话标识符 |
| counterpart | object | 对方参与者 |
| house | object | 相关房源，一般会话可为空 |
| last_message | object | 最新消息摘要 |
| unread_count | int | 此会话中未读消息数 |
| message_count | int | 此会话中消息总数 |

### `GET /api/messages`

获取一个会话的消息。

权限：已认证用户

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| counterpart_id | int | 是 | 对方参与者用户 ID |
| house_id | int | 否 | 可选，限定会话的房源范围 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `POST /api/messages`

向其他用户发送消息。

权限：已认证用户

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| receiver_id | int | 是 | 目标用户 ID |
| content | string | 是 | 消息内容 |
| house_id | int | 否 | 与会话关联的房源 ID，当对话与某个房源相关时提供 |

行为：

1. 发送者不能给自己发消息。
2. 当提供 `house_id` 时，会话必须涉及该房源的房东。
3. 租客向房源房东发起带 `house_id` 的咨询时，系统会基于房源标题、租金、户型、面积、装修和位置生成一条基础自动回复；房东仍可继续人工回复。

### `PATCH /api/messages/read`

将一个会话中的未读消息标记为已读。

权限：已认证用户

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| counterpart_id | int | 是 | 对方参与者用户 ID |
| house_id | int | 否 | 可选，限定会话的房源范围 |

## 维修模块

### `POST /api/repairs`

为有效租赁合同创建维修请求。

权限：仅租客

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| house_id | int | 是 | 当前租客名下有效合同关联的房源 |
| title | string | 是 | 维修标题 |
| description | string | 是 | 维修详情 |
| priority | string | 否 | `low`、`medium`、`high` 或 `urgent`；默认为 `medium` |

### `GET /api/repairs/mine`

获取与当前用户相关的维修请求。

权限：租客、房东或管理员

行为：

1. 租客获取自己提交的维修请求。
2. 房东获取自己房源的维修请求。
3. 管理员获取所有维修请求。

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 否 | 按维修状态筛选 |
| house_id | int | 否 | 按房源筛选 |
| priority | string | 否 | 按优先级筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `PATCH /api/repairs/{repair_id}/status`

更新维修处理状态。

权限：房源所属房东或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 是 | `submitted`、`processing`、`completed` 或 `rejected` |

## 投诉模块

### `POST /api/complaints`

创建投诉。

权限：租客或房东

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| house_id | int | 否 | 相关房源 |
| title | string | 是 | 投诉标题 |
| content | string | 是 | 投诉内容 |

### `GET /api/complaints/mine`

获取投诉记录。

权限：租客、房东或管理员

行为：

1. 租客和房东获取自己提交的投诉。
2. 管理员获取所有投诉。

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 否 | 按投诉状态筛选 |
| house_id | int | 否 | 按房源筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `PATCH /api/complaints/{complaint_id}/status`

更新投诉处理状态和结果。

权限：仅管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 是 | `submitted`、`processing`、`resolved` 或 `rejected` |
| result | string | 否 | 处理结果 |

## 报表模块

### `GET /api/reports/overview`

返回运营统计总数和状态分布。

权限：仅管理员

响应数据包括用户、房源、预约、合同、支付、维修、投诉的总数，已支付金额、待支付金额、出租率、30 天活跃用户、租金收入趋势以及各分组状态计数。

## 监控模块

### `GET /api/monitor/overview`

返回后端服务健康状态、模块状态、检查时间和最近操作日志。

权限：仅管理员

最近日志由关键写操作生成，包括认证、用户状态变更、房源和媒体管理、预约、合同、支付、消息、维修和投诉操作。

## 新闻模块

### `GET /api/news`

获取已发布的新闻和公告。

权限：公开

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| keyword | string | 否 | 搜索标题或内容 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `GET /api/news/mine`

获取管理的新闻记录。

权限：房东或管理员

行为：

1. 房东获取自己撰写的新闻。
2. 管理员获取所有新闻。

查询参数：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 否 | 按状态筛选 |
| keyword | string | 否 | 搜索标题或内容 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页大小 |

### `POST /api/news`

创建新闻或公告条目。

权限：房东或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| title | string | 是 | 新闻标题 |
| content | string | 是 | 新闻内容 |
| status | string | 否 | `draft` 或 `published`；默认为 `draft` |

### `PUT /api/news/{news_id}`

更新标题或内容。

权限：新闻作者房东或管理员

### `PATCH /api/news/{news_id}/status`

更新新闻状态。

权限：新闻作者房东或管理员

请求体：

| 字段 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| status | string | 是 | `draft`、`published` 或 `archived` |

### `DELETE /api/news/{news_id}`

删除新闻条目。

权限：新闻作者房东或管理员

## 错误码建议

| 码 | 含义 |
| --- | --- |
| 0 | 成功 |
| 4001 | 验证错误 |
| 4002 | 认证失败 |
| 4003 | 权限拒绝 |
| 4004 | 资源未找到 |
| 4009 | 资源重复 |
| 4010 | 动态验证码缺失、过期或错误 |
| 5000 | 内部服务器错误 |

## 实现说明

1. 步骤 4 应首先实现 `auth`、`users/profile` 和 `houses`。
2. 后端与前端之间使用一致的序列化字段。
3. 上传和推荐 API 留待迭代增强，而非当前过度设计。
