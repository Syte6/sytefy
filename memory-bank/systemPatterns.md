# System Patterns

- **Architecture**: Clean/Onion layering — `config` (settings), `core` (security/logging/database), `modules/<feature>` (domain, application, infrastructure, web), `shared` (validators/utilities).
- **Security Stack**: HttpOnly JWT cookies with refresh rotation, in-memory refresh session store (Redis-ready), CSP/HSTS headers, rate limiting middleware, optional CSRF protection per environment.
- **Data Access**: SQLAlchemy 2.0 async sessions via PostgreSQL; Alembic maintains schema. Each repository converts ORM models into domain entities.
- **API Composition**: FastAPI routers aggregated under `/api`. Auth router exposes login/register/refresh/logout/me; other feature routers require `get_current_user` dependency.
- **Frontend Pattern**: Next.js app router with feature pages, Tailwind styling, `createClient()` helper that injects `credentials: 'include'` and honors `NEXT_PUBLIC_API_URL`.
