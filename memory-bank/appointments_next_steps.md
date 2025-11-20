# Appointments Gelişim Yol Haritası

## 1. Statü Geçişleri + Reminder Yönetimi
- **Durumların tanımı**: `scheduled`, `confirmed`, `completed`, `cancelled`, `no_show`.
- **Geçiş Kuralları**:
  - `scheduled` → `confirmed` (manuel onay).
  - `confirmed` → `completed` (randevu sonrası).
  - `scheduled|confirmed` → `cancelled` (reminder revoke).
  - `scheduled|confirmed` → `no_show` (otomatik/manual).
  - `completed/cancelled/no_show` geri dönemez; yeni randevu açılmalı.
- **Reminder Davranışı**:
  - `scheduled→confirmed`: reminder eta aynı kalabilir; gerekiyorsa offset yeniden hesaplanır.
  - Statü `cancelled/no_show/completed` olduğunda `reminder_task_id` revoke + `reminder_channels` temizlenir.
  - Gelecekte `confirmed` için farklı offset desteği (örn. 10 dk önce).
- **Test Planı**: Use-case tabanlı unit test (statü geçişi + reminder revoke assertion) ve API testi (PUT + cancel).

## 2. Frontend Entegrasyon Planı
- **Listeleme**: Next.js `/appointments` sayfası, React Query `useAppointments` hook (GET `/api/appointments`).
- **Oluşturma Formu**: `/appointments/new` sayfası, controlled form + `POST /api/appointments`, success sonrası listeyi invalid et.
- **Güncelleme/İptal**: Detay modalı veya `/appointments/[id]`; `PUT` ve `POST /cancel` çağrıları, optimistic UI + toast feedback.
- **State Yönetimi**: React Query + Zod form validation; timezone’lar `luxon` veya `Intl` ile UTC → local dönüşümü.
- **E2E**: Cypress senaryosu (create → edit → cancel) veya Playwright.

## 3. Bildirim Kanalları (Email/SMS)
- **Email**: SMTP veya transactional API (örn. SendGrid). Task `send_appointment_reminder` içinde channel bazlı dispatcher:
  - `if "email" in channels: email_service.send(...)`.
  - Template: JWT veya signed link yok; ICS dosyası üretimi backlog.
- **SMS**: Twilio veya Mock SMS provider; `.env` üzerinden API key, `Settings`te `sms_provider_enabled`.
- **Güvenlik**:
  - Secrets `.env` / Secret Manager, loglarda maskelenmiş.
  - Rate limit + idempotency key (task ID) ile duplicate gönderim engellenir.
- **Testler**: Unit (fake email/SMS client), integration (Celery eager modda log assertion), contract (schema validation).
- **Observability**: Celery task loglarına `channel`, `provider_response`, `retry_count` alanları; Prometheus metric `appointments_reminder_sent_total{channel=...}`.
  - ✅ İlk fazda log tabanlı Email/SMS servisleri ve kontekst payload’ları eklendi; sonraki adım gerçek provider entegrasyonu.

## Öncelik Sırası
1. Statü geçişleri + reminder revoke (backend).
2. Frontend entegrasyonu (listeleme/form).
3. Email/SMS kanalları + gözlemlenebilirlik.
