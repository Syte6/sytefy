# Module Backlog & Next Actions

## Appointments
- ✅ Create/list/update/cancel API + Celery reminders + frontend ekranı.
- 🔜 Ekstra özellikler:
  - Müşteri eşleştirmesi (customer picklist), pagination ve tarih filtreleri.
  - ICS export / calendar sync.
  - Audit log ve kullanıcı bazlı analitikler.

## Services
- Domain: Hizmet paketleri (ad, açıklama, ücret, süre, kategori). Temel CRUD + kategori filtreleri.
- API: `/api/services` (list/create/update/delete). RBAC: owner/admin tam yetki, staff okuma.
- Frontend: Hizmet katalogu ve appointment formu ile entegrasyon (drop-down).
- Data Model: `services (id, user_id, name, description, price_amount, price_currency, duration_minutes, status, created_at, updated_at)`.

## Finances
- Domain: Faturalandırma + ödemeler (invoice, payment, expense). Başlangıçta “Invoices” odaklı.
- API: `/api/finances/invoices` CRUD, PDF export placeholder.
- Integration: Stripe veya mock payment provider; audit + reporting (CSV download).
- Observability: Gelir raporu metric’leri.

## Notifications
- Notification center: persist table `notifications (id, user_id, title, body, channel, read_at)`.
- Providers: Email/SMS/push. İlk fazda Celery tasks + email template (SMTP).
- API: `/api/notifications` list + mark read. Frontend bell icon + toast.
- Security: Rate limit, template sanitization, secret management.

## Delivery Order
1. Services module (backend + minimal frontend select).
2. Notifications persistence + API (email channel as baseline).
3. Finances (invoices) foundation.
