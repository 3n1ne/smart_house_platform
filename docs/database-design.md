# 数据库设计

## 设计目标

此阶段为智能租赁系统建立核心 MySQL 数据模型。设计遵循以下原则：

1. 匹配三种主要角色：房东、租客和管理员。
2. 覆盖完整业务链：房源发布、预约、合同、支付、维修和投诉。
3. 保持 schema 可扩展，以便后续支持智能推荐、多因素认证和审计分析等功能。

## 核心实体关系

1. 一个 `role` 可分配给多个 `user` 记录。
2. 一个房东 `user` 可以发布多个 `house` 记录。
3. 一个 `house` 可以有多个 `house_media`、`booking`、`repair` 和 `complaint` 记录。
4. 一个租客 `user` 可以创建多个 `booking`、`repair` 和 `complaint` 记录。
5. 一个 `contract` 属于一个 `house`、一个房东和一个租客。
6. 一个 `contract` 可以生成多个 `payment` 记录。
7. 用户之间可以通过 `message` 进行交流。
8. 用户操作可被记录在 `operation_log` 中。

## 表概览

### `roles`

存储基于角色的访问控制（RBAC）的角色元数据。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| code | varchar(50) | 唯一角色编码，如 `admin`、`landlord`、`tenant` |
| name | varchar(100) | 角色显示名称 |
| description | varchar(255) | 角色描述 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `users`

存储账户和个人资料信息。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| role_id | bigint | 外键，关联 `roles.id` |
| username | varchar(80) | 唯一登录名 |
| email | varchar(120) | 唯一邮箱，可为空 |
| phone | varchar(20) | 唯一手机号，可为空 |
| password_hash | varchar(255) | 密码哈希 |
| real_name | varchar(80) | 真实姓名 |
| avatar_url | varchar(255) | 头像 URL |
| gender | varchar(20) | 可选性别 |
| identity_no | varchar(255) | 可选身份证号，应用层加密后存储 |
| status | varchar(20) | `active`、`disabled`、`pending` |
| is_mfa_enabled | bool | 多因素认证启用标志 |
| last_login_at | datetime | 最后登录时间 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `houses`

存储房东发布的房源信息。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| landlord_id | bigint | 外键，关联 `users.id` |
| title | varchar(150) | 房源标题 |
| province | varchar(50) | 省份 |
| city | varchar(50) | 城市 |
| district | varchar(50) | 区域 |
| community | varchar(100) | 小区或住宅区 |
| address_detail | varchar(255) | 详细地址 |
| house_type | varchar(50) | 如公寓或整租 |
| layout | varchar(50) | 如 `2室1厅` |
| area | numeric(10,2) | 建筑面积 |
| rent | numeric(10,2) | 月租金 |
| deposit | numeric(10,2) | 押金 |
| decoration | varchar(50) | 装修情况 |
| floor | int | 当前楼层 |
| total_floors | int | 建筑总楼层 |
| orientation | varchar(50) | 房屋朝向 |
| description | text | 房源描述 |
| status | varchar(20) | `draft`、`available`、`rented`、`repairing`、`offline` |
| published_at | datetime | 发布时间 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `house_media`

存储房源的图片和视频。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| house_id | bigint | 外键，关联 `houses.id` |
| media_type | varchar(20) | `image` 或 `video` |
| file_url | varchar(255) | 文件路径或 URL |
| sort_order | int | 排序顺序 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `bookings`

存储看房预约记录。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| house_id | bigint | 外键，关联 `houses.id` |
| tenant_id | bigint | 外键，关联 `users.id` |
| landlord_id | bigint | 外键，关联 `users.id` |
| appointment_time | datetime | 预约看房时间 |
| status | varchar(20) | `pending`、`confirmed`、`cancelled`、`completed` |
| remark | varchar(255) | 租客备注 |
| confirmed_at | datetime | 确认时间 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `contracts`

存储已签署的租赁合同。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| contract_no | varchar(64) | 唯一合同编号 |
| house_id | bigint | 外键，关联 `houses.id` |
| landlord_id | bigint | 外键，关联 `users.id` |
| tenant_id | bigint | 外键，关联 `users.id` |
| start_date | date | 租赁开始日期 |
| end_date | date | 租赁结束日期 |
| monthly_rent | numeric(10,2) | 合同月租金 |
| deposit | numeric(10,2) | 合同押金 |
| payment_cycle | varchar(20) | 如 `monthly` |
| status | varchar(20) | `draft`、`signed`、`active`、`expired`、`terminated` |
| signed_at | datetime | 签署时间 |
| content | text | 合同内容 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `payments`

存储租金和押金支付记录。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| contract_id | bigint | 外键，关联 `contracts.id` |
| payer_id | bigint | 外键，关联 `users.id` |
| payee_id | bigint | 外键，关联 `users.id` |
| amount | numeric(10,2) | 支付金额 |
| payment_type | varchar(20) | `rent`、`deposit`、`refund`、`other` |
| payment_method | varchar(30) | 如 `alipay`、`wechat`、`bank` |
| transaction_no | varchar(100) | 第三方交易号 |
| due_date | date | 支付截止日期 |
| paid_at | datetime | 支付时间 |
| status | varchar(20) | `pending`、`paid`、`failed`、`refunded`、`overdue` |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `messages`

存储房东与租客的沟通记录。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| sender_id | bigint | 外键，关联 `users.id` |
| receiver_id | bigint | 外键，关联 `users.id` |
| house_id | bigint | 可选外键，关联 `houses.id` |
| content | text | 消息内容 |
| is_read | bool | 已读标志 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `news`

存储房东公告或租赁相关通知。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| author_id | bigint | 外键，关联 `users.id` |
| title | varchar(150) | 新闻标题 |
| content | text | 新闻内容 |
| status | varchar(20) | `draft`、`published`、`archived` |
| published_at | datetime | 发布时间 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `repairs`

存储租客的维修请求。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| house_id | bigint | 外键，关联 `houses.id` |
| tenant_id | bigint | 外键，关联 `users.id` |
| handler_id | bigint | 可选外键，关联 `users.id` |
| title | varchar(150) | 维修标题 |
| description | text | 维修描述 |
| priority | varchar(20) | `low`、`medium`、`high`、`urgent` |
| status | varchar(20) | `submitted`、`accepted`、`processing`、`completed`、`rejected` |
| handled_at | datetime | 处理开始时间 |
| completed_at | datetime | 完成时间 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `complaints`

存储服务或房源投诉。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| house_id | bigint | 可选外键，关联 `houses.id` |
| complainant_id | bigint | 外键，关联 `users.id` |
| handler_id | bigint | 可选外键，关联 `users.id` |
| title | varchar(150) | 投诉标题 |
| content | text | 投诉内容 |
| status | varchar(20) | `submitted`、`processing`、`resolved`、`rejected` |
| result | text | 处理结果 |
| handled_at | datetime | 处理时间 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### `operation_logs`

存储审计和监控记录。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | bigint | 主键 |
| operator_id | bigint | 可选外键，关联 `users.id` |
| module | varchar(50) | 模块名称 |
| action | varchar(50) | 操作类型 |
| target_type | varchar(50) | 业务对象类型 |
| target_id | bigint | 业务对象 ID |
| ip_address | varchar(45) | 客户端 IP |
| user_agent | varchar(255) | 客户端 User Agent |
| detail | text | 额外操作详情 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 推荐索引

1. `users.username`、`users.email`、`users.phone`
2. `houses.landlord_id`、`houses.city`、`houses.district`、`houses.layout`、`houses.status`
3. `bookings.house_id`、`bookings.tenant_id`、`bookings.landlord_id`、`bookings.status`
4. `contracts.house_id`、`contracts.landlord_id`、`contracts.tenant_id`、`contracts.contract_no`
5. `payments.contract_id`、`payments.status`、`payments.due_date`
6. `messages.sender_id`、`messages.receiver_id`、`messages.house_id`
7. `repairs.status`、`complaints.status`、`operation_logs.module`

## 下一轮迭代注意事项

1. 添加迁移支持和角色的初始种子数据。
2. 身份证号已通过应用层加密存储，并在 API 响应中只返回脱敏值；生产环境建议将 `SENSITIVE_DATA_KEY` 托管到 KMS 或密钥管理服务。
3. 基于这些实体定义 API 请求和响应结构。
