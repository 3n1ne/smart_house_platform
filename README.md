# Smart Rental System

Vue 3 + Flask + MySQL based smart house rental system.

## Structure

- `backend/`: Flask backend project
- `frontend/`: Vue 3 frontend project
- `docs/`: requirement decomposition, database design, and API notes

## Current Progress

1. Initial project scaffold completed.
2. Database design and backend model skeleton completed.
3. Core REST API contract design completed.
4. Frontend authentication flow and house browsing pages connected to backend APIs.
5. Landlord-side house management page connected to house management APIs.
6. Booking workflow connected across backend APIs and frontend tenant/landlord dashboards.
7. Contract creation, contract signing, and payment workflow connected across backend APIs and frontend dashboards.
8. Repair, complaint, report, and monitor workflows connected across backend APIs and role dashboards.
9. Real house media upload, preview, and deletion connected for landlord-side house management.
10. Operation logging connected for key write actions and surfaced through the admin monitor overview.
11. Admin user management connected for role/status/keyword filtering and account enable/disable operations.
12. News and announcement management connected for landlord/admin publishing and public announcement browsing.
13. Backend testing infrastructure added with SQLite-based pytest coverage for authentication, house publishing/browsing, and news lifecycle APIs.
14. Alembic migration baseline added with core schema and role seed data, plus end-to-end rental workflow API coverage.

## Backend Migrations

Run database migrations from the `backend/` directory:

```powershell
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
$env:DATABASE_URI = "mysql+pymysql://user:password@host:3306/rent_house"
..\.venv\Scripts\flask.exe --app run:app db upgrade
```

## Iteration Plan

1. Design the database schema.
2. Define the REST API contract.
3. Implement authentication and house management modules.
4. Implement rental workflow, messaging, and maintenance modules.
5. Improve reporting, monitoring, and deployment support.
6. Expand automated tests and add Alembic migration scripts for production schema management.
7. Add deployment configuration, seed/admin bootstrap strategy, and broader regression coverage.
