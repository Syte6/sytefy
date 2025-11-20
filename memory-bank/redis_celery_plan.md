# Redis Oturum Deposu + Celery Hatırlatıcı Tasarımı

## Redis Refresh Session Store
- **Hedef**: In-memory `RefreshSessionStore` sınıfını Redis destekli hale getirip çoklu instance senaryolarında tutarlı oturum iptali sağlamak.
- **Arayüz**: Mevcut API korunacak (`remember`, `is_active`, `revoke`, `revoke_all_for_user`). Yeni sınıf `RedisRefreshSessionStore`, `core/security/sessions.py` içinde veya ayrı dosyada tanımlanacak ve `IAccessSessionStore` benzeri bir protokole bağlanacak.
- **Bağımlılık**: `redis.asyncio.Redis` kullan, `Settings.redis_url` ile konfigüre et. Bağlantı factory'si (`get_redis_client`) `core/cache` altında tutulabilir, Dependency Injection ile `get_session_store` fonksiyonuna enjekte edilir.
- **Veri Modeli**:
  - Key formatı: `refresh:{jti}` → değer JSON (`{"uid": <int>, "exp": "<iso8601>"}`) veya sadece `user_id`.
  - TTL: `expires_at` ile hesaplanıp Redis `setex` kullanılarak otomatik purge edilir.
  - `revoke_all_for_user`: `SCAN` + `DEL` yerine `refresh_user:{user_id}` set'i tutulur. `remember` sırasında `SADD refresh_user:{user_id} jti` yapılır; revoke ederken `SREM` + `DEL`.
- **Hata Dayanıklılığı**:
  - Redis hatası durumunda `ApplicationError` değil, `HTTP 500` döndür.
  - Bağlantı düşerse logla ve `False` döndürerek fail-closed davran (refresh başarısız olur, kullanıcı tekrar login olmalı).
- **Test Planı**:
  - Unit: `FakeRedis` ile TTL ve JTI silme senaryosu.
  - Integration: `/auth/refresh` rotası Redis store ile çalışırken concurrency testi. pytest'te `redis.asyncio.Redis` yerine `fakeredis` injection yapılacak.

## Celery Hatırlatıcı Scheduler
- **Amaç**: Randevu/finans hatırlatıcılarını zamanında göndermek (e-posta/SMS placeholders).
- **Mimari**:
  - Celery app `sytefy_backend.worker` modülünde oluşturulacak, konfig `settings.redis_url` (broker) + `settings.celery_backend_url`.
  - Task modülleri Clean Architecture'ı bozmayacak şekilde `modules/<feature>/tasks.py` altında domain içi servisleri çağıracak (ör: `appointments.tasks.send_followup_reminder`).
  - FastAPI tarafında planlanan hatırlatmalar `celery_app.send_task` veya `task.apply_async(eta=...)` ile planlanacak.
- **Hatırlatıcı Akışı**:
  1. Kullanıcı randevu oluşturduğunda `ScheduleReminder` use-case’i Celery task'ini enqueue eder (`eta = appointment.time - settings.reminder_offset_minutes`).
  2. Task çalıştığında domain servisinden gerekli veriyi çeker (repo read-only), bildirimi üretir, şu an için sadece log yazar; gelecekte e-posta/SMS entegre edilecek.
  3. Task başarısızsa Celery auto-retry (örn. 3 deneme, exponential backoff).
- **Konfig Parametreleri**:
  - `CELERY_BROKER_URL`, `CELERY_BACKEND_URL`, `REMINDER_OFFSET_MINUTES`, `REMINDER_MAX_RETRIES`.
  - Docker Compose’a `celery_worker` ve `celery_beat` servisleri eklenecek; Redis hem broker hem oturum deposu olarak kullanılabilir ancak ileride RabbitMQ desteği için soyutlama bırak.
- **Gözlemlenebilirlik**:
  - Celery tasks structlog kullanmalı, `task_name`, `appointment_id`, `retry` alanlarını loglasın.
  - Task metrikleri Prometheus’a köprülemek için `celery_prometheus_exporter` entegrasyonu veya custom collector planlandı.
- **Durum**: Celery worker (`sytefy_backend.worker`), hatırlatıcı görevi (`appointments.send_reminder`) ve `ScheduleAppointmentReminder` use-case’i eklendi; sonraki adım gerçek bildirim kanallarını bağlamak.

## Riskler & Sonraki Adımlar
- Redis yokken backend fallback olarak in-memory store kullanmaya devam etmeli (feature flag).
- Celery dev ortamında opsiyonel olmalı; tasks dev modda synchronous (`CELERY_TASK_ALWAYS_EAGER=True`) çalışabilir.
- Follow-up: `core/security/sessions.py` içerisinde interface soyutlaması + dependency injection, Celery uygulaması için `worker.py` + docker-compose güncellemesi.
