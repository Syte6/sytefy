# Sytefy Backend

Modern FastAPI uygulaması; Clean Architecture katmanları ve PostgreSQL/Redis entegrasyonu içerir.

## Kurulum
1. `cd backend`
2. `poetry install`
3. `.env` dosyasını `.env.example` üzerinden oluşturun (CORS origin'lerini virgülle ayırın).
4. Veritabanını hazırlayın:
   ```bash
   poetry run alembic upgrade head
   ```
5. `poetry run uvicorn sytefy_backend.app.main:app --reload`

## Testler
`poetry run pytest`

## Migrasyonlar
- Yeni migrasyon: `poetry run alembic revision --autogenerate -m "message"`
- Uygulama: `poetry run alembic upgrade head`

## Docker
`docker-compose up --build backend` komutu Postgres, Redis ve FastAPI servislerini birlikte çalıştırır.

## Celery Worker
- Geliştirmede eşzamanlı görev yürütme: `poetry run celery -A sytefy_backend.worker.celery_app worker -l info`
- Docker Compose üzerinde `celery_worker` servisi aynı komutu çalıştırır; broker/backend olarak Redis kullanır.

## Gözlemlenebilirlik
- FastAPI, `/metrics` ucunda Prometheus formatında HTTP metriklerini ve Celery hatırlatıcı sayaçlarını sunar:
  - `sytefy_requests_total`, `sytefy_request_duration_seconds` (HTTP katmanı)
  - `sytefy_reminder_tasks_total{status=started|succeeded|failed}`
  - `sytefy_reminder_channel_events_total{channel=\"email\"|\"sms\"|\"notification\", status=\"sent\"|\"failed\"}`
- Yerel doğrulama:
  ```bash
  curl -s http://127.0.0.1:8000/metrics | grep sytefy_reminder
  ```
- Prometheus veya başka bir collector bu endpoint’i scrape ederek dashboard/alarmlar tanımlayabilir.
