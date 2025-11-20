## Bildirim Merkezi QA Notları

- `npm run dev` ile frontend’i çalıştır ve tarayıcıda `/notifications` sayfasını aç.
- Backend’de bir randevu oluşturup reminder tetikle; başarılı/başarısız kanallar Notification listesinde yeni satır olarak görünmeli.
- “Okundu işaretle” butonu ile kaydı güncelle; eleman listeden kaybolmaz fakat `Okundu` tarihi güncellenir ve buton gizlenir.
- API hatası tetiklemek için backend’i kapatıp sayfayı yenile; kırmızı hata mesajı çıktığını doğrula.

## Prometheus /metrics QA
## Prometheus /metrics QA

- Backend çalışırken `curl -s http://127.0.0.1:8000/metrics | grep sytefy_reminder` komutunu çalıştır.
- Celery reminder tetiklendiğinde `sytefy_reminder_tasks_total{status="started"}` ve `status="succeeded"` sayaçlarının arttığını gözlemle.
- Email/SMS denemesi için `sytefy_reminder_channel_events_total{channel="email",status="sent"}` (veya `failed`) satırlarını kontrol et; değerler >=1 olmalı.

## ICS Export QA

- API’den bir randevu oluşturduktan sonra `GET /api/appointments/{id}/ics` çağrısını yap (`curl -H "Cookie: ..." http://127.0.0.1:8000/api/appointments/1/ics`).
- Dönen `text/calendar` içeriğinde `BEGIN:VEVENT`, `SUMMARY:<başlık>`, `DTSTART/DTEND` satırlarının bulunduğunu ve tarayıcı indirmenin `.ics` uzantılı olduğunu doğrula.
