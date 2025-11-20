# Progress Log

## Completed
- Clean backend skeleton (settings, core security, FastAPI app) with in-memory rate limiting & secure headers.
- Auth module: register/login/refresh/logout, HttpOnly cookies, refresh-session store, `/auth/me` guard.
- Customers module: CRUD foundations + frontend `/customers` status page.
- Users module basics: `/users/me` GET/PUT using profile repository; frontend `/settings` page hitting API.
- RBAC katmanı: Roles tablosu + varsayılan roller, admin kullanıcı listesi ve rol/MFA güncelleme uçları, testler.
- Observability v1: Prometheus metrikleri, `/metrics` ucu ve yapılandırılmış request logları.
- Redis tabanlı refresh session store (opsiyonel backend seçimi) + fakeredis testleri.
- Celery altyapısı: merkezi worker, randevu hatırlatıcı görevleri, programlama use-case’i ve compose entegrasyonu.
- Appointments v1: Alembic tablosu, repository/use-case katmanları, `/api/appointments` POST/GET/PUT/cancel uçları ve pytest senaryoları.
- Appointments state machine: statü geçiş kuralları, reminder revoke/reschedule mantığı ve ApplicationError–>HTTP 400 eşlemeleri.
- Appointments frontend: Next.js sayfası ile listeleme, oluşturma formu, statü güncelleme/iptal aksiyonları ve React Query cache invalidasyonu.
- Services modülü: domain/repository/use-case + `/api/services` CRUD uçları (owner/admin yetkili) ve pytest senaryosu.
- Notifications v1: tablo + repository + `/api/notifications` list/create/read uçları, Celery dispatcher ve testler.
- Appointment reminders now ship with email/SMS channel abstractions, contextual payloads, and Celery task logging + coverage.
- Gerçek provider entegrasyonları: SMTP tabanlı e-posta ve Twilio uyumlu SMS servisleri + config/env ayarları, Celery reminder task’ine bağlandı ve pytest senaryosu ile doğrulandı.
- Reminder teslimat sonuçları Notification kaydına işleniyor; kullanıcının `/notifications` listesinden email/SMS gönderimlerinin başarı/başarısız statüsünü takip etmesi sağlandı.
- Frontend bildirim merkezi sayfası eklendi (`/notifications`), unread counter + “Okundu” aksiyonu ve QA notlarıyla doğrulama yönergeleri hazır.
- Celery reminder görevleri Prometheus sayaçlarıyla enstrümante edildi; kanal bazlı `sytefy_reminder_channel_events_total` ve görev sonuçlarını izleyen `sytefy_reminder_tasks_total` metrikleri `/metrics` çıktısına ekledi.
- Appointments için ICS export: `/api/appointments/{id}/ics` uç noktası metin/takvim dosyası döndürüyor, frontend’de download linki gösterilecek; pytest senaryosu eklendi (şimdilik SQLite kısıtından ötürü CI dışında çalıştırılamıyor).
- Finances modülü temel haliyle eklendi: Invoices domain/use-case/repo/REST uçları + Alembic migrasyonu, frontend’den bağımsız test senaryosu (yerel Postgres erişimi gerektiğinden doğrulama beklemede).
- Frontend finans sayfası (`/finances`) React Query ile fatura listeleme, form üzerinden oluşturma ve “ödendi” işaretleme akışlarını sunuyor; navigasyona Finans bağlantısı eklendi.

## In Progress
- Reminder kanallarının üretim ortamında gerçek provider’lara bağlanması ve frontend notifikasyon beslemesi; worker gözlemi ve alert’leri bağlamak.

## Outstanding
- Appointments/services/finances/notifications modules.
- Bildirim kanalları (e-posta/SMS), reminder cancel/retry stratejileri, Redis oturum deposu failover planları.
- Observability (Prometheus + structured logging shipping) and full test suite (≥80% coverage across modules).
