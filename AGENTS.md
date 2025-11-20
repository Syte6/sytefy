# Repository Guidelines

## Project Structure & Module Organization
Root folders separate concerns: `backend/` contains the FastAPI service with Clean Architecture layers in `src/sytefy_backend/{app,core,modules,shared}` and domain slices such as `modules/{auth,users,customers}`. Database migrations sit in `backend/alembic`, while tests and fixtures live in `backend/tests`. `frontend/src` holds the Next.js app router and Tailwind UI, and `docker-compose.yml` orchestrates PostgreSQL, Redis, and the API for local runs.

## Build, Test, and Development Commands
- `docker-compose up --build backend` boots Postgres, Redis, and FastAPI.
- `cd backend && poetry install && cp .env.example .env` installs deps; `poetry run uvicorn sytefy_backend.app.main:app --reload` starts the API server.
- `poetry run alembic upgrade head` applies migrations; `poetry run pytest` executes backend unit and async integration suites.
- `cd frontend && npm install && npm run dev` launches the Next.js dev server, while `npm run build` and `npm run lint` gate production readiness.

## Coding Style & Naming Conventions
Python targets 3.11, uses 4-space indentation, explicit type hints, and strict layer boundaries (entities in `core`, use-cases in `modules`, adapters in `shared`). Suffix service classes and routers with `Service`/`Router`, expose Pydantic models in PascalCase (e.g., `AuthTokenResponse`), and run `poetry run ruff check --fix` before commits. Frontend files are TypeScript-first: components use PascalCase filenames, hooks are camelCase, and `next lint` enforces ESLint + TypeScript rules.

## Testing Guidelines
Place tests in `backend/tests/<module>/test_<feature>.py` and name functions `test_<behavior>__should_<expectation>` for clarity. Prefer `pytest-asyncio` with AsyncClient fixtures when hitting FastAPI routers, and assert happy path plus auth/validation failures to keep modules near 80% coverage. Cover schema changes with migration tests, and ensure UI work passes `npm run lint` and adds manual QA notes or component-level tests when logic changes.

## Commit & Pull Request Guidelines
Write imperative, scope-focused commit titles (`Add auth refresh tokens`) and keep each commit limited to one module or migration; include ticket IDs or context in the body. PRs must outline the problem, explain key changes, list verification commands (`poetry run pytest`, `npm run lint`), and attach screenshots or GIFs for UI updates. Call out new environment variables or breaking changes directly in the PR description.

## Security & Configuration Tips
Copy `.env.example` files per service instead of editing secrets in place, and never commit populated `.env` assets. Configuration flows through `sytefy_backend.config.settings`, so extend pydantic Settings classes instead of hardcoding URLs or keys. Use SQLAlchemy parameterization, respect CORS/JWT defaults, and run `docker-compose down --volumes` when rotating local data.
