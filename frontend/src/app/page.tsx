'use client';

import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import { createClient } from '../lib/api';

const client = createClient();

export default function HomePage() {
  const { data, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: () => client.get('/health'),
  });

  const status = useMemo(() => {
    if (isLoading) return 'Kontrol ediliyor...';
    return data?.status === 'ok' ? 'API hazır' : 'API ulaşılamıyor';
  }, [isLoading, data]);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 p-8">
      <div className="text-center space-y-2">
        <p className="text-sm uppercase tracking-wide text-slate-400">Sytefy</p>
        <h1 className="text-4xl font-bold">Dijital Sekreter Kontrol Paneli</h1>
        <p className="text-lg text-slate-300 max-w-2xl">
          FastAPI + Next.js tabanlı yeni mimari, güvenlik katmanları ve modüler yapıyla yeniden inşa ediliyor.
        </p>
      </div>
      <div className="bg-slate-900/60 border border-slate-700 rounded-2xl px-8 py-6 shadow-lg">
        <p className="text-sm text-slate-400">Backend durumu</p>
        <p className="text-2xl font-semibold mt-2">{status}</p>
      </div>
    </main>
  );
}
