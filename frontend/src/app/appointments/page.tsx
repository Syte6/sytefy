'use client';

import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createClient } from '../../lib/api';

type Appointment = {
  id: number;
  title: string;
  description?: string | null;
  location?: string | null;
  channel: string;
  start_at: string;
  end_at: string;
  status: string;
  reminder_channels: string[];
};
type AppointmentListResponse = {
  items: Appointment[];
  total: number;
};

type CreateFormState = {
  title: string;
  description: string;
  location: string;
  channel: string;
  startAt: string;
  endAt: string;
  reminderChannels: Set<string>;
};

const client = createClient();
const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api';
const statusLabels: Record<string, string> = {
  scheduled: 'Planlandı',
  confirmed: 'Onaylandı',
  completed: 'Tamamlandı',
  cancelled: 'İptal',
  no_show: 'Gelmedi',
};

function formatDate(value: string) {
  const date = new Date(value);
  return new Intl.DateTimeFormat('tr-TR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export default function AppointmentsPage() {
  const queryClient = useQueryClient();
  const [formState, setFormState] = useState<CreateFormState>({
    title: '',
    description: '',
    location: '',
    channel: 'in_person',
    startAt: '',
    endAt: '',
    reminderChannels: new Set(['log']),
  });
  const [formMessage, setFormMessage] = useState<string | null>(null);

  const [page, setPage] = useState(0);
  const limit = 5;
  const { data, isLoading, error } = useQuery({
    queryKey: ['appointments', page, limit],
    queryFn: () => client.get<AppointmentListResponse>(`/appointments/?limit=${limit}&offset=${page * limit}`),
    keepPreviousData: true,
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      if (!formState.startAt || !formState.endAt) {
        throw new Error('Başlangıç ve bitiş zamanı zorunludur.');
      }
      const payload = {
        title: formState.title,
        description: formState.description || undefined,
        location: formState.location || undefined,
        channel: formState.channel,
        start_at: new Date(formState.startAt).toISOString(),
        end_at: new Date(formState.endAt).toISOString(),
        reminder_channels: Array.from(formState.reminderChannels),
      };
      await client.post('/appointments/', payload);
    },
    onSuccess: () => {
      setFormMessage('Randevu oluşturuldu.');
      setFormState({
        title: '',
        description: '',
        location: '',
        channel: 'in_person',
        startAt: '',
        endAt: '',
        reminderChannels: new Set(['log']),
      });
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
    },
    onError: (err) => setFormMessage(err instanceof Error ? err.message : 'Randevu oluşturulamadı.'),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => client.put(`/appointments/${id}`, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['appointments'] }),
  });

  const cancelMutation = useMutation({
    mutationFn: (id: number) => client.post(`/appointments/${id}/cancel`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['appointments'] }),
  });

  const appointments = useMemo(() => data?.items ?? [], [data]);
  const sortedAppointments = useMemo(
    () => [...appointments].sort((a, b) => (a.start_at > b.start_at ? 1 : -1)),
    [appointments]
  );

  const handleReminderToggle = (value: string) => {
    setFormState((prev) => {
      const next = new Set(prev.reminderChannels);
      if (next.has(value)) {
        next.delete(value);
      } else {
        next.add(value);
      }
      return { ...prev, reminderChannels: next };
    });
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white p-10 space-y-8">
      <header className="space-y-2">
        <p className="text-sm uppercase text-slate-400">Sytefy</p>
        <h1 className="text-3xl font-bold">Randevu Takvimi</h1>
        <p className="text-slate-400">API tabanlı randevu planlama, durum güncelleme ve hatırlatma yönetimi.</p>
      </header>

      <section className="grid gap-6 md:grid-cols-2">
        <form
          className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            createMutation.mutate();
          }}
        >
          <div>
            <label className="text-sm text-slate-400 block mb-1">Başlık</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
              value={formState.title}
              onChange={(e) => setFormState((prev) => ({ ...prev, title: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="text-sm text-slate-400 block mb-1">Açıklama</label>
            <textarea
              className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
              value={formState.description}
              onChange={(e) => setFormState((prev) => ({ ...prev, description: e.target.value }))}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-slate-400 block mb-1">Konum</label>
              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
                value={formState.location}
                onChange={(e) => setFormState((prev) => ({ ...prev, location: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 block mb-1">Kanal</label>
              <select
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
                value={formState.channel}
                onChange={(e) => setFormState((prev) => ({ ...prev, channel: e.target.value }))}
              >
                <option value="in_person">Yüz yüze</option>
                <option value="video">Video</option>
                <option value="phone">Telefon</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-slate-400 block mb-1">Başlangıç</label>
              <input
                type="datetime-local"
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
                value={formState.startAt}
                onChange={(e) => setFormState((prev) => ({ ...prev, startAt: e.target.value }))}
                required
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 block mb-1">Bitiş</label>
              <input
                type="datetime-local"
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
                value={formState.endAt}
                onChange={(e) => setFormState((prev) => ({ ...prev, endAt: e.target.value }))}
                required
              />
            </div>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-2">Hatırlatma Kanalları</p>
            <div className="flex gap-4 flex-wrap">
              {['log', 'email', 'sms'].map((channel) => (
                <label key={channel} className="inline-flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={formState.reminderChannels.has(channel)} onChange={() => handleReminderToggle(channel)} />
                  {channel.toUpperCase()}
                </label>
              ))}
            </div>
          </div>
          {formMessage && <p className="text-sm text-slate-300">{formMessage}</p>}
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="w-full rounded-lg bg-emerald-600 py-2 font-semibold hover:bg-emerald-500 disabled:opacity-50"
          >
            {createMutation.isPending ? 'Kaydediliyor...' : 'Randevu Oluştur'}
          </button>
        </form>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-3">
          <h2 className="text-xl font-semibold">Duruma göre filtre</h2>
          <p className="text-sm text-slate-400">Filtreleme opsiyonları yakında burada olacak.</p>
        </section>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Yaklaşan Randevular</h2>
        {isLoading && <p className="text-slate-400">Yükleniyor...</p>}
        {error && <p className="text-red-400">{error instanceof Error ? error.message : 'Veri alınamadı.'}</p>}
        {!isLoading && !error && sortedAppointments.length === 0 && (
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-slate-300">Henüz randevu yok.</div>
        )}
        <div className="grid gap-4">
          {sortedAppointments.map((appointment) => (
            <div key={appointment.id} className="rounded-xl border border-slate-800 bg-slate-900/80 p-6 space-y-3">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h3 className="text-xl font-semibold">{appointment.title}</h3>
                  <p className="text-sm text-slate-400">
                    {formatDate(appointment.start_at)} · {statusLabels[appointment.status] ?? appointment.status}
                  </p>
                </div>
                <div className="flex gap-2">
                  {appointment.status === 'scheduled' && (
                    <button
                      className="rounded-lg border border-emerald-500 px-3 py-1 text-sm hover:bg-emerald-500/10"
                      disabled={statusMutation.isPending}
                      onClick={() => statusMutation.mutate({ id: appointment.id, status: 'confirmed' })}
                    >
                      Onayla
                    </button>
                  )}
                  {['scheduled', 'confirmed'].includes(appointment.status) && (
                    <button
                      className="rounded-lg border border-sky-500 px-3 py-1 text-sm hover:bg-sky-500/10"
                      disabled={statusMutation.isPending}
                      onClick={() => statusMutation.mutate({ id: appointment.id, status: 'completed' })}
                    >
                      Tamamlandı
                    </button>
                  )}
                  {['scheduled', 'confirmed'].includes(appointment.status) && (
                    <button
                      className="rounded-lg border border-red-500 px-3 py-1 text-sm hover:bg-red-500/10"
                      disabled={cancelMutation.isPending}
                      onClick={() => cancelMutation.mutate(appointment.id)}
                    >
                      İptal Et
                    </button>
                  )}
                  <a
                    className="rounded-lg border border-slate-600 px-3 py-1 text-sm hover:bg-slate-700/60"
                    href={`${apiBaseUrl}/appointments/${appointment.id}/ics`}
                  >
                    ICS İndir
                  </a>
                </div>
              </div>
              {appointment.description && <p className="text-slate-300">{appointment.description}</p>}
              <div className="text-sm text-slate-400">
                <p>Konum: {appointment.location || 'Belirtilmedi'}</p>
                <p>
                  Hatırlatma:{' '}
                  {appointment.reminder_channels.length > 0
                    ? appointment.reminder_channels.map((channel) => channel.toUpperCase()).join(', ')
                    : 'Yok'}
                </p>
              </div>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-between pt-4 text-sm text-slate-300">
          <div>
            Toplam kayıt:{' '}
            <span className="font-semibold">{data?.total ?? (sortedAppointments.length > 0 ? sortedAppointments.length : 0)}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="rounded-lg border border-slate-600 px-3 py-1 disabled:opacity-40"
              onClick={() => setPage((prev) => Math.max(prev - 1, 0))}
              disabled={page === 0}
            >
              Önceki
            </button>
            <span>Sayfa {page + 1}</span>
            <button
              className="rounded-lg border border-slate-600 px-3 py-1 disabled:opacity-40"
              onClick={() => setPage((prev) => prev + 1)}
              disabled={!data || data.items.length < limit}
            >
              Sonraki
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
