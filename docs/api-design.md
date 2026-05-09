# API Design

## Design Scope

This document defines the first-round REST API contract for the smart rental system. It focuses on the modules that will be implemented first:

1. Authentication
2. User profile
3. House management
4. Search and house display
5. Booking
6. Contract
7. Payment
8. Message
9. Repair
10. Complaint
11. Report
12. Monitor
13. News

## Common Rules

### Base Path

All APIs use the `/api` prefix.

### Response Format

Success response:

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

Failure response:

```json
{
  "code": 4001,
  "message": "validation error",
  "errors": {
    "field": ["error detail"]
  }
}
```

### Authentication

1. Use JWT for authenticated requests.
2. Client sends token through `Authorization: Bearer <token>`.
3. Role-based permissions are enforced for landlord, tenant, and admin routes.

### Pagination Convention

List APIs accept:

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| page | int | 1 | Current page |
| page_size | int | 10 | Page size |

Paginated response:

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

## Authentication Module

### `POST /api/auth/register`

Register a new user account.

Allowed roles for initial registration: `landlord`, `tenant`

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| role | string | yes | `landlord` or `tenant` |
| username | string | yes | Unique username |
| password | string | yes | Plain password before hashing |
| email | string | no | Email |
| phone | string | no | Phone |
| real_name | string | no | Real name |

Response data:

| Field | Type | Description |
| --- | --- | --- |
| user_id | int | Created user ID |
| username | string | Username |
| role | string | User role |

### `POST /api/auth/login`

Authenticate user and return JWT.

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| username | string | yes | Username or phone or email |
| password | string | yes | Plain password |

Response data:

| Field | Type | Description |
| --- | --- | --- |
| access_token | string | JWT access token |
| token_type | string | Usually `Bearer` |
| user | object | Basic user info |

### `GET /api/auth/me`

Return current authenticated user info.

Permission: authenticated user

### `POST /api/auth/logout`

Current phase will keep this as a logical logout endpoint for frontend integration. Token blacklist can be added later.

Permission: authenticated user

## User Module

### `GET /api/users/profile`

Get current user profile.

Permission: authenticated user

Response fields:

| Field | Type | Description |
| --- | --- | --- |
| id | int | User ID |
| username | string | Username |
| role | string | Role code |
| email | string | Email |
| phone | string | Phone |
| real_name | string | Real name |
| avatar_url | string | Avatar URL |
| status | string | User status |

### `PUT /api/users/profile`

Update current user profile.

Permission: authenticated user

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| real_name | string | no | Real name |
| email | string | no | Email |
| phone | string | no | Phone |
| avatar_url | string | no | Avatar URL |
| gender | string | no | Gender |

### `GET /api/users`

Get user list.

Permission: admin only

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| role | string | no | Filter by role |
| status | string | no | Filter by status |
| keyword | string | no | Username, real name, phone |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `PATCH /api/users/{user_id}/status`

Update user status.

Permission: admin only

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | yes | `active` or `disabled` |

Frontend admin dashboard now consumes these APIs for role/status/keyword filtering and account enable/disable operations.

## House Module

### `POST /api/houses`

Create a new house listing.

Permission: landlord only

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| title | string | yes | Listing title |
| province | string | no | Province |
| city | string | yes | City |
| district | string | yes | District |
| community | string | no | Community |
| address_detail | string | yes | Detailed address |
| house_type | string | no | House type |
| layout | string | yes | Layout |
| area | number | yes | Area |
| rent | number | yes | Monthly rent |
| deposit | number | no | Deposit |
| decoration | string | no | Decoration |
| floor | int | no | Floor |
| total_floors | int | no | Total floors |
| orientation | string | no | Orientation |
| description | string | no | Description |

### `GET /api/houses`

Get public house list.

Permission: public

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| city | string | no | City filter |
| district | string | no | District filter |
| layout | string | no | Layout filter |
| min_rent | number | no | Minimum rent |
| max_rent | number | no | Maximum rent |
| status | string | no | Default to `available` for public list |
| keyword | string | no | Search title or address |
| page | int | no | Page number |
| page_size | int | no | Page size |

Response item fields:

| Field | Type | Description |
| --- | --- | --- |
| id | int | House ID |
| title | string | Listing title |
| city | string | City |
| district | string | District |
| layout | string | Layout |
| area | number | Area |
| rent | number | Monthly rent |
| status | string | House status |
| cover_url | string | Primary image URL |

### `GET /api/houses/mine`

Get current landlord's managed house list.

Permission: landlord or admin

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | no | Filter by house status |
| city | string | no | Filter by city |
| keyword | string | no | Search title, community, or address |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `GET /api/houses/{house_id}`

Get house detail.

Permission: public

### `PUT /api/houses/{house_id}`

Update a house listing.

Permission: landlord owner only

### `DELETE /api/houses/{house_id}`

Delete or logically offline a house listing.

Permission: landlord owner or admin

### `PATCH /api/houses/{house_id}/status`

Update house status.

Permission: landlord owner or admin

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | yes | `draft`, `available`, `rented`, `repairing`, `offline` |

### `POST /api/houses/{house_id}/media`

Upload house media. Supports both multipart file upload and external media URL metadata.

Permission: landlord owner only

JSON request body for external media:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| media_type | string | yes | `image` or `video` |
| file_url | string | yes | Uploaded file URL |
| sort_order | int | no | Sort order |

Multipart form data for local upload:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| file | file | yes | Image or video file |
| sort_order | int | no | Sort order |

Uploaded files are served from `/uploads/<path>`.

### `DELETE /api/houses/{house_id}/media/{media_id}`

Delete a house media record. If the media file is stored under the local upload folder, the file is removed as well.

Permission: landlord owner or admin

## Search Module

### `GET /api/search/regions`

Aggregate houses by region.

Permission: public

Response item fields:

| Field | Type | Description |
| --- | --- | --- |
| city | string | City |
| district | string | District |
| community | string | Community |
| house_count | int | Matching house count |

### `GET /api/search/layouts`

Aggregate houses by layout.

Permission: public

Response item fields:

| Field | Type | Description |
| --- | --- | --- |
| layout | string | House layout |
| house_count | int | Matching house count |

### `GET /api/search/recommendations`

Return recommended houses. Current phase can use rule-based recommendation such as latest houses or similar price range.

Permission: public

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| house_id | int | no | Base house for similar recommendation |
| city | string | no | City filter |
| limit | int | no | Number of results |

## Booking Module

### `POST /api/bookings`

Create a new house viewing booking.

Permission: tenant only

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| house_id | int | yes | Target house ID |
| appointment_time | string | yes | ISO datetime string |
| remark | string | no | Booking note |

### `GET /api/bookings/mine`

Get booking records for current user.

Permission: tenant, landlord, or admin

Behavior:

1. Tenant gets bookings created by self.
2. Landlord gets bookings for own houses.
3. Admin gets all bookings.

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | no | Filter by booking status |
| house_id | int | no | Filter by house |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `PATCH /api/bookings/{booking_id}/status`

Update booking status.

Permission:

1. Landlord owner or admin can set `confirmed`, `cancelled`, `completed`.
2. Tenant can only set `cancelled` for own booking.

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | yes | `confirmed`, `cancelled`, or `completed` |

## Contract Module

### `POST /api/contracts`

Create a rental contract from an eligible booking.

Permission: landlord or admin

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| booking_id | int | yes | Confirmed or completed booking ID |
| start_date | string | yes | Lease start date in `YYYY-MM-DD` |
| end_date | string | yes | Lease end date in `YYYY-MM-DD` |
| payment_cycle | string | no | Defaults to `monthly` |
| content | string | no | Contract content |

### `GET /api/contracts/mine`

Get contracts related to current user.

Permission: tenant, landlord, or admin

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | no | Filter by contract status |
| house_id | int | no | Filter by house |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `PATCH /api/contracts/{contract_id}/sign`

Tenant signs the prepared contract.

Permission: tenant or admin

Behavior:

1. Contract must be in `draft` status.
2. On success, contract becomes `active`.
3. Initial pending payments are generated automatically.

### `PATCH /api/contracts/{contract_id}/status`

Update contract lifecycle status.

Permission: landlord owner or admin

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | yes | `terminated` or `expired` |

## Payment Module

### `GET /api/payments/mine`

Get payments relevant to current user.

Permission: tenant, landlord, or admin

Behavior:

1. Tenant gets payments where current user is payer.
2. Landlord gets payments where current user is payee.
3. Admin gets all payments.

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | no | Filter by payment status |
| contract_id | int | no | Filter by contract |
| payment_type | string | no | Filter by payment type |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `PATCH /api/payments/{payment_id}/pay`

Mark a payment as paid.

Permission: payer or admin

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| payment_method | string | yes | Such as `bank`, `alipay`, or `wechat` |
| transaction_no | string | no | Optional transaction reference |

## Message Module

### `GET /api/messages/conversations`

Get the current user's conversation summary list.

Permission: authenticated user

Response data:

| Field | Type | Description |
| --- | --- | --- |
| conversation_key | string | Conversation identifier composed from house and counterpart |
| counterpart | object | The other participant |
| house | object | Related house, nullable for general conversation |
| last_message | object | Latest message summary |
| unread_count | int | Unread messages in this conversation |
| message_count | int | Total messages in this conversation |

### `GET /api/messages`

Get messages for one conversation.

Permission: authenticated user

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| counterpart_id | int | yes | The other participant user ID |
| house_id | int | no | Optional house scope for the conversation |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `POST /api/messages`

Send a message to another user.

Permission: authenticated user

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| receiver_id | int | yes | Target user ID |
| content | string | yes | Message content |
| house_id | int | no | Related house ID when the conversation is tied to a listing |

Behavior:

1. Sender cannot message self.
2. When `house_id` is provided, the conversation must involve that house's landlord.

### `PATCH /api/messages/read`

Mark unread messages in one conversation as read.

Permission: authenticated user

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| counterpart_id | int | yes | The other participant user ID |
| house_id | int | no | Optional house scope for the conversation |

## Repair Module

### `POST /api/repairs`

Create a repair request for an active rental contract.

Permission: tenant only

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| house_id | int | yes | House under an active contract owned by current tenant |
| title | string | yes | Repair title |
| description | string | yes | Repair details |
| priority | string | no | `low`, `medium`, `high`, or `urgent`; defaults to `medium` |

### `GET /api/repairs/mine`

Get repair requests relevant to current user.

Permission: tenant, landlord, or admin

Behavior:

1. Tenant gets repair requests submitted by self.
2. Landlord gets repair requests for own houses.
3. Admin gets all repair requests.

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | no | Filter by repair status |
| house_id | int | no | Filter by house |
| priority | string | no | Filter by priority |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `PATCH /api/repairs/{repair_id}/status`

Update repair handling status.

Permission: landlord owner or admin

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | yes | `submitted`, `processing`, `completed`, or `rejected` |

## Complaint Module

### `POST /api/complaints`

Create a complaint.

Permission: tenant or landlord

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| house_id | int | no | Related house |
| title | string | yes | Complaint title |
| content | string | yes | Complaint content |

### `GET /api/complaints/mine`

Get complaint records.

Permission: tenant, landlord, or admin

Behavior:

1. Tenant and landlord get complaints submitted by self.
2. Admin gets all complaints.

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | no | Filter by complaint status |
| house_id | int | no | Filter by house |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `PATCH /api/complaints/{complaint_id}/status`

Update complaint processing status and result.

Permission: admin only

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | yes | `submitted`, `processing`, `resolved`, or `rejected` |
| result | string | no | Processing result |

## Report Module

### `GET /api/reports/overview`

Return operational totals and status distributions.

Permission: admin only

Response data includes user, house, booking, contract, payment, repair, complaint totals, paid amount, pending payment amount, and grouped status counts.

## Monitor Module

### `GET /api/monitor/overview`

Return backend service health, module status, check time, and recent operation logs.

Permission: admin only

Recent logs are generated by key write actions, including authentication, user status changes, house and media management, booking, contract, payment, message, repair, and complaint operations.

## News Module

### `GET /api/news`

Get published news and announcements.

Permission: public

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| keyword | string | no | Search title or content |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `GET /api/news/mine`

Get managed news records.

Permission: landlord or admin

Behavior:

1. Landlord gets news authored by self.
2. Admin gets all news.

Query params:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | no | Filter by status |
| keyword | string | no | Search title or content |
| page | int | no | Page number |
| page_size | int | no | Page size |

### `POST /api/news`

Create a news or announcement item.

Permission: landlord or admin

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| title | string | yes | News title |
| content | string | yes | News content |
| status | string | no | `draft` or `published`; defaults to `draft` |

### `PUT /api/news/{news_id}`

Update title or content.

Permission: landlord author or admin

### `PATCH /api/news/{news_id}/status`

Update news status.

Permission: landlord author or admin

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| status | string | yes | `draft`, `published`, or `archived` |

### `DELETE /api/news/{news_id}`

Delete a news item.

Permission: landlord author or admin

## Error Code Suggestion

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 4001 | Validation error |
| 4002 | Authentication failed |
| 4003 | Permission denied |
| 4004 | Resource not found |
| 4009 | Duplicate resource |
| 5000 | Internal server error |

## Notes For Implementation

1. Step 4 should implement `auth`, `users/profile`, and `houses` first.
2. Use consistent serialization fields between backend and frontend.
3. Reserve upload and recommendation APIs for iterative enhancement rather than over-designing them now.
