# Tech Context

- **Backend**: Python 3.11, FastAPI 0.115, SQLAlchemy 2.0 (async), Alembic 1.13, PostgreSQL, Redis (future), pytest + pytest-asyncio.
- **Security Libraries**: python-jose for JWT, bcrypt for hashing, custom middleware for rate limiting/security headers.
- **Frontend**: Next.js 14 App Router, React 18, Tailwind CSS, @tanstack/react-query for data fetching.
- **Tooling**: Docker Compose (postgres, redis, backend), Poetry for dependency management, ESLint/Tailwind configs for frontend.
- **Constraints**: No external services (SendGrid/Twilio) wired yet; memory bank must track architecture decisions; CI expected to enforce ≥80% coverage.
