# Sytefy Platformu

FastAPI + Next.js tabanlı, temiz mimarili ve güvenlik odaklı dijital sekreter uygulaması.

## Yapı
```
sytefy/
├── backend/          # FastAPI, PostgreSQL, Redis entegrasyonu
├── frontend/         # Next.js 14 + React 18 + Tailwind
└── docker-compose.yml
```

## Başlangıç
1. `docker-compose up --build backend` ile Postgres, Redis ve FastAPI servislerini birlikte başlatın.
2. Backend için:
   ```bash
   cd backend
   poetry install
   cp .env.example .env
   poetry run alembic upgrade head
   poetry run uvicorn sytefy_backend.app.main:app --reload
   ```
3. Frontend için:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Mimari İlkeler
- Clean Architecture katmanları (`core`, `modules`, `shared`).
- PostgreSQL + SQLAlchemy 2.0 + async session + Alembic migrasyonları.
- OWASP uyumlu güvenlik katmanı (CSP, rate limiting, JWT, güçlü parolalar).
- Modüler geliştirme: ilk modül `auth`, sırada `users`, `customers`, `appointments`, `finances`.
