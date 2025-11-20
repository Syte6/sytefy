# Active Context

- **Current Focus**: Hatırlatıcı kanalları (log/email/SMS) gerçek provider ayarlarıyla çalışıyor; reminder sonuçlarını Notification akışına işlemek tamamlandı, şimdi frontend bildirimi ve gözlem katmanı güçlendirilecek.
- **Recent Changes**:
  - RBAC + MFA readiness delivered; Redis tabanlı refresh session store devrede.
  - Prometheus gözlemlenebilirliği ve `/metrics` ucu hazır.
  - Celery altyapısı + randevu hatırlatıcı görevleri (create/list/update/cancel uçları ile) implemente edildi.
  - Appointment reminder scheduler artık müşteri/owner kontekstini taşıyor; SMTP e-posta + Twilio uyumlu SMS servisleri gerçek provider ayarlarıyla entegre edildi, reminder sonuçları Notifications tablosuna yansıtılıyor ve pytest senaryoları güncellendi.
- **Next Steps**:
  1. Frontend bildirim ikonunu/listesini reminder statüleriyle senkronize et; kullanıcıya email/SMS sonuçlarını göster.
  2. Prod/staging’de provider kimlik bilgilerini ekleyip uçtan uca doğrulama yap (SMTP/Twilio).
  3. Worker gözlemlenebilirliğini (Prometheus exporter) genişlet, alarm koşullarını tanımla.
- **Considerations**:
  - Frontend-host hizalaması ve cookie paylaşımı halen kritik (127.0.0.1 kullanımı).
  - Celery production’da Redis’e bağlı; broker/worker gözlemi için log + metrics takibi şart.
