# Development Progress

## Current Stage

Project is being developed incrementally. Each completed step updates this document and related design files.

## Step Status

| Step | Status | Description |
| --- | --- | --- |
| 1 | Completed | Build initial project structure |
| 2 | Completed | Complete database design and backend model skeleton |
| 3 | Completed | Define REST API contract |
| 4 | Completed | Implement authentication and house management |
| 5 | Completed | Implement booking, contract, payment, and messaging |
| 6 | Completed | Implement repair, complaint, report, and monitor |
| 7 | Completed | Implement media upload, operation logging, admin users, and news |
| 8 | Completed | Add backend test infrastructure and initial regression coverage |
| 9 | Completed | Add Alembic migration baseline and end-to-end rental workflow coverage |

## Step 2 Output

1. Added `docs/database-design.md` to describe core entities, relationships, and fields.
2. Upgraded backend models from placeholders to actual SQLAlchemy model definitions.
3. Prepared the project for the next step: API contract design.

## Step 3 Output

1. Added `docs/api-design.md` to define the first-round REST API contract.
2. Standardized response structure, pagination, permission scope, and suggested error codes.
3. Clarified the implementation boundary for the next coding step.

## Step 4 Output So Far

1. Added common response helpers and role-based access control helpers.
2. Implemented backend APIs for registration, login, current user, profile update, user management, and house management.
3. Added startup role seeding so the initial role data is available in development.
4. Added frontend API request scaffolding for auth and house modules.
5. Added Vite entry page and API proxy configuration for local frontend-backend development.
6. Implemented frontend auth store, route guards, login/register pages, and house list/detail pages.
7. Installed frontend dependencies and verified successful Vite production build.
8. Added landlord house management API and connected landlord dashboard for create, edit, status change, and offline operations.
9. Added booking module API design and started the booking workflow implementation.
10. Implemented booking APIs, tenant booking submission from house detail, tenant booking list, and landlord booking processing UI.
11. Verified booking backend files with `py_compile` and the frontend with a successful Vite build.
12. Added contract and payment API design, serialization, and backend endpoints.
13. Extended tenant and landlord dashboards for contract creation, signing, payment listing, and payment completion.
14. Verified contract/payment backend files with `py_compile` and the frontend with a successful Vite build.

## Step 5 Output

15. Implemented backend messaging APIs for conversation summaries, message history, sending messages, and marking unread messages as read.
16. Added a tenant-side listing contact form so house inquiries can start directly from the house detail page.
17. Added a shared landlord/tenant dashboard message center with unread counts as the current notification flow.
18. Updated API documentation for the new messaging module.

## Step 6 Output

19. Implemented backend repair APIs for tenant submission, role-scoped listing, and landlord/admin status handling.
20. Implemented backend complaint APIs for user submission, admin listing, and admin resolution handling.
21. Added admin report and monitor overview APIs for operational totals, status distribution, service health, and recent logs.
22. Connected tenant dashboard repair and complaint submission plus progress tracking.
23. Connected landlord dashboard repair work order handling.
24. Connected admin dashboard report, monitor, and complaint handling views.
25. Verified Step 6 backend files with `py_compile` and the frontend with a successful Vite build.

## Step 7 Output

26. Extended house media API to accept multipart image/video uploads while preserving external media URL support.
27. Added uploaded media serving through `/uploads/<path>` and configurable `UPLOAD_FOLDER` / `MAX_CONTENT_LENGTH`.
28. Added house media deletion with local uploaded file cleanup.
29. Connected landlord dashboard media upload, thumbnail preview, and media deletion controls.
30. Added Vite proxy support for `/uploads` during local development.
31. Verified updated backend files with `py_compile` and the frontend with a successful Vite build.

## Step 8 Output

32. Added a shared operation logging helper for request IP, user agent, operator, module, action, target, and structured detail.
33. Connected operation logging to registration, login, profile updates, admin user status updates, house management, media management, booking changes, contract changes, payment completion, message sending, repair handling, and complaint handling.
34. The admin monitor overview now has real operation data to display through existing recent log output.
35. Verified backend modules with `compileall`, route registration, and a successful frontend Vite build.

## Step 9 Output

36. Added frontend user API helpers for admin user list and account status updates.
37. Rebuilt the admin dashboard with readable Chinese copy and a user management section.
38. Connected role, status, and keyword filtering for users.
39. Connected admin enable/disable account actions with report and monitor refresh after updates.
40. Verified backend modules with `compileall` and the frontend with a successful Vite build.

## Step 10 Output

41. Replaced the news placeholder API with public published-news listing and landlord/admin management APIs.
42. Added news serialization, operation logging, status lifecycle, and keyword filtering.
43. Added public `/news` page and top-level navigation entry for published announcements.
44. Added a shared news management component and embedded it in landlord and admin dashboards.
45. Extended report and monitor overview data to include the news module.
46. Verified backend modules with `compileall`, route registration, and the frontend with a successful Vite build.

## Step 11 Output

47. Added a dedicated testing configuration that uses an in-memory SQLite database and isolated upload folder overrides.
48. Added SQLite-compatible model ID typing while preserving MySQL `BIGINT` primary keys for the target database.
49. Added pytest coverage for registration/login/current-user APIs, landlord house publishing and public browsing, tenant house permission checks, and news publication visibility.
50. Centralized UTC timestamp generation to remove `datetime.utcnow()` deprecation warnings in Python 3.12+.
51. Added `pytest` to backend dependencies.
52. Verified backend modules with `compileall`, backend API tests with `pytest`, and the frontend with a successful Vite build.

## Step 12 Output

53. Added a Flask-Migrate/Alembic migration repository under `backend/migrations`.
54. Added the initial production schema migration covering roles, users, houses, media, bookings, contracts, payments, messages, news, repairs, complaints, and operation logs.
55. Seeded the initial `admin`, `landlord`, and `tenant` roles through the first migration.
56. Made `AUTO_CREATE_DB` environment-driven and disabled it by default for production so production schema management can move through migrations.
57. Updated `run.py` to select the Flask config from `FLASK_CONFIG`, which makes CLI migration usage predictable.
58. Added an end-to-end rental workflow API test for house publishing, booking, booking confirmation, contract creation, contract signing, payment generation, and payment completion.
59. Verified Alembic upgrade/role seed/downgrade against a temporary SQLite database, then verified backend tests, backend compilation, and frontend production build.

## Next Step

Continue with deployment configuration, admin bootstrap/seed strategy, broader regression coverage, and text encoding cleanup.
