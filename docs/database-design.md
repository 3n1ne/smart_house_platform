# Database Design

## Design Goal

This phase establishes the core MySQL data model for the smart rental system. The design follows these principles:

1. Match the three main roles: landlord, tenant, and administrator.
2. Cover the full business chain: house listing, booking, contract, payment, repair, and complaint.
3. Keep the schema extensible for later features such as smart recommendation, MFA, and audit analysis.

## Core Entity Relationship

1. One `role` can be assigned to many `user` records.
2. One landlord `user` can publish many `house` records.
3. One `house` can have many `house_media`, `booking`, `repair`, and `complaint` records.
4. One tenant `user` can create many `booking`, `repair`, and `complaint` records.
5. One `contract` belongs to one `house`, one landlord, and one tenant.
6. One `contract` can generate many `payment` records.
7. Users can communicate through `message`.
8. User actions can be tracked in `operation_log`.

## Table Overview

### `roles`

Stores role metadata for RBAC.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| code | varchar(50) | Unique role code, such as `admin`, `landlord`, `tenant` |
| name | varchar(100) | Role display name |
| description | varchar(255) | Role description |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `users`

Stores account and profile information.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| role_id | bigint | FK to `roles.id` |
| username | varchar(80) | Unique login name |
| email | varchar(120) | Unique email, nullable |
| phone | varchar(20) | Unique phone, nullable |
| password_hash | varchar(255) | Password hash |
| real_name | varchar(80) | Real name |
| avatar_url | varchar(255) | Avatar URL |
| gender | varchar(20) | Optional gender |
| identity_no | varchar(64) | Optional identity number |
| status | varchar(20) | `active`, `disabled`, `pending` |
| is_mfa_enabled | bool | MFA enabled flag |
| last_login_at | datetime | Last login time |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `houses`

Stores property listings published by landlords.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| landlord_id | bigint | FK to `users.id` |
| title | varchar(150) | Listing title |
| province | varchar(50) | Province |
| city | varchar(50) | City |
| district | varchar(50) | District |
| community | varchar(100) | Community or residential area |
| address_detail | varchar(255) | Full address detail |
| house_type | varchar(50) | Such as apartment or whole-rent |
| layout | varchar(50) | Such as `2室1厅` |
| area | numeric(10,2) | Building area |
| rent | numeric(10,2) | Monthly rent |
| deposit | numeric(10,2) | Deposit |
| decoration | varchar(50) | Decoration status |
| floor | int | Current floor |
| total_floors | int | Building total floors |
| orientation | varchar(50) | House orientation |
| description | text | House description |
| status | varchar(20) | `draft`, `available`, `rented`, `repairing`, `offline` |
| published_at | datetime | Publish time |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `house_media`

Stores pictures and videos for a house.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| house_id | bigint | FK to `houses.id` |
| media_type | varchar(20) | `image` or `video` |
| file_url | varchar(255) | File path or URL |
| sort_order | int | Sort order |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `bookings`

Stores house viewing appointments.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| house_id | bigint | FK to `houses.id` |
| tenant_id | bigint | FK to `users.id` |
| landlord_id | bigint | FK to `users.id` |
| appointment_time | datetime | Requested viewing time |
| status | varchar(20) | `pending`, `confirmed`, `cancelled`, `completed` |
| remark | varchar(255) | Tenant remark |
| confirmed_at | datetime | Confirmation time |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `contracts`

Stores signed rental contracts.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| contract_no | varchar(64) | Unique contract number |
| house_id | bigint | FK to `houses.id` |
| landlord_id | bigint | FK to `users.id` |
| tenant_id | bigint | FK to `users.id` |
| start_date | date | Lease start date |
| end_date | date | Lease end date |
| monthly_rent | numeric(10,2) | Monthly rent in contract |
| deposit | numeric(10,2) | Deposit in contract |
| payment_cycle | varchar(20) | Such as `monthly` |
| status | varchar(20) | `draft`, `signed`, `active`, `expired`, `terminated` |
| signed_at | datetime | Sign time |
| content | text | Contract content |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `payments`

Stores rent and deposit payment records.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| contract_id | bigint | FK to `contracts.id` |
| payer_id | bigint | FK to `users.id` |
| payee_id | bigint | FK to `users.id` |
| amount | numeric(10,2) | Payment amount |
| payment_type | varchar(20) | `rent`, `deposit`, `refund`, `other` |
| payment_method | varchar(30) | Such as `alipay`, `wechat`, `bank` |
| transaction_no | varchar(100) | Third-party transaction number |
| due_date | date | Payment due date |
| paid_at | datetime | Payment time |
| status | varchar(20) | `pending`, `paid`, `failed`, `refunded`, `overdue` |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `messages`

Stores landlord and tenant communication records.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| sender_id | bigint | FK to `users.id` |
| receiver_id | bigint | FK to `users.id` |
| house_id | bigint | Optional FK to `houses.id` |
| content | text | Message content |
| is_read | bool | Read flag |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `news`

Stores landlord announcements or rental-related notices.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| author_id | bigint | FK to `users.id` |
| title | varchar(150) | News title |
| content | text | News content |
| status | varchar(20) | `draft`, `published`, `archived` |
| published_at | datetime | Publish time |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `repairs`

Stores repair requests from tenants.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| house_id | bigint | FK to `houses.id` |
| tenant_id | bigint | FK to `users.id` |
| handler_id | bigint | Optional FK to `users.id` |
| title | varchar(150) | Repair title |
| description | text | Repair description |
| priority | varchar(20) | `low`, `medium`, `high`, `urgent` |
| status | varchar(20) | `submitted`, `accepted`, `processing`, `completed`, `rejected` |
| handled_at | datetime | Handling start time |
| completed_at | datetime | Completion time |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `complaints`

Stores service or listing complaints.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| house_id | bigint | Optional FK to `houses.id` |
| complainant_id | bigint | FK to `users.id` |
| handler_id | bigint | Optional FK to `users.id` |
| title | varchar(150) | Complaint title |
| content | text | Complaint content |
| status | varchar(20) | `submitted`, `processing`, `resolved`, `rejected` |
| result | text | Processing result |
| handled_at | datetime | Handling time |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

### `operation_logs`

Stores audit and monitoring records.

| Field | Type | Description |
| --- | --- | --- |
| id | bigint | Primary key |
| operator_id | bigint | Optional FK to `users.id` |
| module | varchar(50) | Module name |
| action | varchar(50) | Action type |
| target_type | varchar(50) | Business object type |
| target_id | bigint | Business object ID |
| ip_address | varchar(45) | Client IP |
| user_agent | varchar(255) | Client user agent |
| detail | text | Extra operation detail |
| created_at | datetime | Creation time |
| updated_at | datetime | Update time |

## Recommended Indexes

1. `users.username`, `users.email`, `users.phone`
2. `houses.landlord_id`, `houses.city`, `houses.district`, `houses.layout`, `houses.status`
3. `bookings.house_id`, `bookings.tenant_id`, `bookings.landlord_id`, `bookings.status`
4. `contracts.house_id`, `contracts.landlord_id`, `contracts.tenant_id`, `contracts.contract_no`
5. `payments.contract_id`, `payments.status`, `payments.due_date`
6. `messages.sender_id`, `messages.receiver_id`, `messages.house_id`
7. `repairs.status`, `complaints.status`, `operation_logs.module`

## Notes For Next Iteration

1. Add migration support and initial seed data for roles.
2. Confirm which fields require encryption at rest.
3. Define API request and response structures based on these entities.
