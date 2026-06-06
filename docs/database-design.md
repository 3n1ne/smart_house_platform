# 数据库设计

数据库使用 MySQL，表结构由 Alembic 迁移管理。模型代码位于 `backend/app/models/`，迁移脚本位于 `backend/migrations/versions/`。

## 核心关系

系统围绕三类用户展开：管理员、房东、租客。

1. `roles` 定义角色，`users.role_id` 关联角色。
2. 房东 `users` 可以发布多个 `houses`。
3. `houses` 可以关联图片视频、预约、维修和投诉。
4. 租客可以创建预约、维修和投诉。
5. `contracts` 连接房源、房东和租客。
6. `payments` 属于合同，用于租金、押金和退款记录。
7. `messages` 记录用户间沟通。
8. `operation_logs` 记录关键业务操作。

## 表概览

| 表 | 用途 | 关键字段 |
| --- | --- | --- |
| `roles` | RBAC 角色 | `code`、`name` |
| `users` | 登录账号和个人资料 | `role_id`、`username`、`password_hash`、`status`、`identity_no` |
| `houses` | 房东发布的房源 | `landlord_id`、`city`、`district`、`layout`、`rent`、`status` |
| `house_media` | 房源图片和视频 | `house_id`、`media_type`、`file_url` |
| `bookings` | 看房预约 | `house_id`、`tenant_id`、`landlord_id`、`appointment_time`、`status` |
| `contracts` | 租赁合同 | `contract_no`、`house_id`、`tenant_id`、`landlord_id`、`status` |
| `payments` | 租金、押金和退款 | `contract_id`、`payer_id`、`payee_id`、`amount`、`status` |
| `messages` | 用户消息 | `sender_id`、`receiver_id`、`house_id`、`is_read` |
| `news` | 公告和资讯 | `author_id`、`title`、`status`、`published_at` |
| `repairs` | 维修请求 | `house_id`、`tenant_id`、`handler_id`、`priority`、`status` |
| `complaints` | 投诉处理 | `house_id`、`complainant_id`、`handler_id`、`status` |
| `operation_logs` | 审计日志 | `operator_id`、`module`、`action`、`target_type`、`target_id` |

## 主要状态

| 字段 | 取值 |
| --- | --- |
| `users.status` | `active`、`disabled`、`pending` |
| `houses.status` | `draft`、`available`、`rented`、`repairing`、`offline` |
| `bookings.status` | `pending`、`confirmed`、`cancelled`、`completed` |
| `contracts.status` | `draft`、`signed`、`active`、`expired`、`terminated` |
| `payments.status` | `pending`、`paid`、`failed`、`refunded`、`overdue` |
| `repairs.status` | `submitted`、`accepted`、`processing`、`completed`、`rejected` |
| `complaints.status` | `submitted`、`processing`、`resolved`、`rejected` |
| `news.status` | `draft`、`published`、`archived` |

## 安全字段

`users.password_hash` 只保存密码哈希。`users.identity_no` 用于保存加密后的身份证号，API 响应只返回脱敏值。生产环境必须设置独立的 `SENSITIVE_DATA_KEY`，不要使用示例值。

## 推荐索引

| 表 | 索引建议 |
| --- | --- |
| `users` | `username`、`email`、`phone` 唯一索引 |
| `houses` | `landlord_id`、`city`、`district`、`layout`、`status` |
| `bookings` | `house_id`、`tenant_id`、`landlord_id`、`status` |
| `contracts` | `contract_no`、`house_id`、`tenant_id`、`landlord_id` |
| `payments` | `contract_id`、`status`、`due_date` |
| `messages` | `sender_id`、`receiver_id`、`house_id` |
| `repairs` / `complaints` | `status`、处理人和提交人相关字段 |
| `operation_logs` | `module`、`action`、`operator_id` |

## 迁移版本

| 版本 | 说明 |
| --- | --- |
| `20260509_0001` | 初始 schema，包含核心业务表和基础角色 |
| `20260521_0002` | 扩展 `users.identity_no` 字段长度 |

迁移操作见 [数据库迁移](database-migration.md)。
