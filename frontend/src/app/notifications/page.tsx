'use client';

import { useMemo } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createClient } from '../../lib/api';

type Notification = {
  id: number;
  title: string;
  body: string;
  channel: string;
  status: string;
  read_at?: string | null;
  created_at?: string | null;
};

const client = createClient();

const channelLabels: Record<string, string> = {
  email: 'E-posta',
  sms: 'SMS',
  log: 'Log',
  notification: 'Uygulama',
};

const statusClasses: Record<string, string> = {
  pending: 'bg-amber-500/20 text-amber-200 border border-amber-500/30',
  sent: 'bg-emerald-500/20 text-emerald-200 border border-emerald-500/30',
  read: 'bg-slate-600/30 text-slate-200 border border-slate-600/40',
  failed: 'bg-rose-500/20 text-rose-200 border border-rose-500/30',
};

const statusLabels: Record<string, string> = {
  pending: 'Beklemede',
  sent: 'Gönderildi',
  read: 'Okundu',
  failed: 'Hata',
};

function formatDate(value?: string | null) {
  if (!value) return '—';
  const date = new Date(value);
  return new Intl.DateTimeFormat('tr-TR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

function StatusBadge({ status }: { status: string }) {
  const label = statusLabels[status] ?? status;
  const klass = statusClasses[status] ?? 'bg-slate-700/40 text-white border border-slate-600/30';
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${klass}`}>{label}</span>;
}

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => client.get<Notification[]>('/notifications/'),
    refetchInterval: 10000,
    refetchOnWindowFocus: true,
  });

  const markReadMutation = useMutation({
    mutationFn: (id: number) => client.post(`/notifications/${id}/read`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const notifications = useMemo(() => data ?? [], [data]);
  const unreadCount = notifications.filter((item) => !item.read_at).length;

  return (
    <main className="min-h-screen bg-slate-950 text-white p-10 space-y-8">
      <header className="space-y-2">
        <p className="text-sm uppercase text-slate-400">Sytefy</p>
        <h1 className="text-3xl font-bold">Bildirim Merkezi</h1>
        <p className="text-slate-400">
          Randevu hatırlatma kanallarından gelen e-posta/SMS sonuçlarını ve uygulama bildirimlerini buradan takip edin.
        </p>
        <div className="text-sm text-slate-400">
          Okunmamış bildirim sayısı:{' '}
          <span className="text-white font-semibold">{isLoading ? '—' : unreadCount}</span>
        </div>
      </header>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60">
        <div className="border-b border-slate-800 px-6 py-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-semibold">Bildirimler</p>
            <p className="text-sm text-slate-400">Son gönderim denemeleri kronolojik olarak listelenir.</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              className="inline-flex items-center rounded-lg border border-slate-600 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-800/80"
              onClick={() => refetch()}
              disabled={isLoading}
            >
              {isLoading ? 'Yükleniyor...' : 'Yenile'}
            </button>
          </div>
        </div>
        <div className="divide-y divide-slate-800">
          {isLoading && <div className="px-6 py-8 text-slate-400">Yükleniyor...</div>}
          {error && !isLoading && (
            <div className="px-6 py-8 text-rose-300">Bildirimler yüklenemedi: {(error as Error).message}</div>
          )}
          {!isLoading && !error && notifications.length === 0 && (
            <div className="px-6 py-8 text-slate-400">Henüz bildirim yok.</div>
          )}
          {!isLoading &&
            !error &&
            notifications.map((notification) => (
              <article key={notification.id} className="px-6 py-5 flex flex-col gap-2 md:flex-row md:items-center">
                <div className="flex-1 space-y-1">
                  <div className="flex flex-wrap items-center gap-3">
                    <p className="font-semibold text-lg">{notification.title}</p>
                    <StatusBadge status={notification.status} />
                    <span className="text-xs uppercase text-slate-400 tracking-wide">
                      {channelLabels[notification.channel] ?? notification.channel}
                    </span>
                  </div>
                  <p className="text-sm text-slate-300 whitespace-pre-line">{notification.body}</p>
                  <div className="text-xs text-slate-500">
                    Gönderim: {formatDate(notification.created_at)} · Okundu: {formatDate(notification.read_at)}
                  </div>
                </div>
                {!notification.read_at && (
                  <button
                    className="mt-2 md:mt-0 inline-flex items-center gap-2 rounded-lg border border-emerald-400/40 px-3 py-2 text-sm text-emerald-200 hover:bg-emerald-500/10"
                    onClick={() => markReadMutation.mutate(notification.id)}
                    disabled={markReadMutation.isPending}
                  >
                    {markReadMutation.isPending ? 'İşleniyor...' : 'Okundu işaretle'}
                  </button>
                )}
              </article>
            ))}
        </div>
      </section>
    </main>
  );
}
