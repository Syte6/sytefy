# Appointments Modülü Planı

## Domain Model
- **Appointment**: `id`, `user_id`, `customer_id`, `title`, `description`, `location`, `start_at`, `end_at`, `status` (scheduled, completed, cancelled), `channel` (phone, video, in-person), `created_at`, `updated_at`.
- **Reminder**: Ayrık tabloya gerek yok; appointment satırı `remind_at` + `reminder_channels` (JSON) alanları içerir, Celery scheduling bu alanları kullanır.
- **Invariants**:
  - `start_at < end_at`
  - Kullanıcı/müşteri foreign key’leri zorunlu, `customer_id` opsiyonel olabilir fakat B2B senaryolarında genelde zorunlu.
  - Cancelled randevularda reminder queue iptal edilir (`revoke_all_for_user` benzeri task cancel hook gerekebilir).

## Katmanlar
- **Domain**: `Appointment` entity + value objects (ör. `AppointmentChannel` enum).
- **Application** Use Cases:
  1. `CreateAppointment` – Customer repo + reminder scheduler (opsiyonel).
  2. `ListAppointments` – filtreler: tarih aralığı, durum, müşteri.
  3. `UpdateAppointment` – statü/slot güncellemeleri + reminder re-schedule.
  4. `CancelAppointment` – reminder revoke + audit log.
  5. `ScheduleReminder` – mevcut use-case ile entegre (appointment kaydı sırasında veya manuel).
- **Infrastructure**:
  - ORM modeli `appointments` tablosunda saklanacak (SQLAlchemy).
  - Repository `AppointmentRepository` use-case’lere domain entity dönecek.
  - Celery adaptörü mevcut `CeleryReminderTaskClient` ile paylaşılır.

## API Katmanı
- `POST /appointments`: doğrulama + `CreateAppointment` çağrısı; isteğe bağlı `remind_at` override.
- `GET /appointments`: pagination + filtre query parametreleri.
- `PUT /appointments/{id}`: slot güncelleme; reminder replan et.
- `POST /appointments/{id}/cancel`: status=cancelled, reminder revoke.

## Veri Modeli & Migrasyon
```
appointments (
  id SERIAL PK,
  user_id INT FK -> users,
  customer_id INT FK -> customers,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  location VARCHAR(255),
  channel VARCHAR(20) NOT NULL DEFAULT 'in_person',
  start_at TIMESTAMP WITH TIME ZONE NOT NULL,
  end_at TIMESTAMP WITH TIME ZONE NOT NULL,
  remind_at TIMESTAMP WITH TIME ZONE,
  reminder_channels JSONB,
  status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
)
```

## Reminder Akışı
1. `CreateAppointment` → validasyon + repo insert.
2. `ScheduleAppointmentReminder` offset kullanarak `remind_at` belirler, task ID’yi randevu satırına yazar (`reminder_task_id`).
3. Update/cancel senaryolarında task iptali için Celery `revoke` veya custom store; minimal viable: reminder offset her güncellemede yeniden planlanır, iptal durumunda task ID kaydı tutulup `celery_app.control.revoke`.

## Riskler & Gelişim Adımları
- Task ID saklanmazsa iptal etmek zor; tabloya `reminder_task_id` alanı eklendi ve revoke akışı tamamlandı.
- Saat dilimi yönetimi: bütün tarih alanları UTC stored, frontend locale conversion yapar.
- Celery eager modda localde sorunsuz; prod’da broker latency loglanmalı.
- Durum: `appointments` tablosu, repository/use-case (create/list/update/cancel) ve `/api/appointments` uçları eklendi; reminder_task_id kalıcı, revoke destekli. Sonraki sprint: status transition kuralları, frontend entegrasyonu ve gerçek notification kanalları.
