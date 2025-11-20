'use client';

import { useEffect, useState } from 'react';
import { createClient } from '../../lib/api';

type Customer = {
  id: number;
  name: string;
  email?: string | null;
  phone?: string | null;
};

const api = createClient();

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading');
  const [message, setMessage] = useState<string>('Müşteri listesi yükleniyor...');

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get<Customer[]>('/customers/');
        setCustomers(data);
        setStatus('ready');
      } catch (error) {
        setStatus('error');
        setMessage(
          error instanceof Error
            ? error.message
            : 'Müşteri verileri alınırken bir hata oluştu. Oturum açtığınızdan emin olun.'
        );
      }
    }
    load();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-white p-10 space-y-6">
      <header>
        <p className="text-sm uppercase text-slate-400">Sytefy</p>
        <h1 className="text-3xl font-bold">Müşteri Yönetimi</h1>
        <p className="text-slate-400">
          FastAPI API&apos;sinden alınan veriler yalnızca doğrulanmış tarayıcı oturumlarıyla yüklenir.
        </p>
      </header>

      {status === 'error' && (
        <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4">
          <p className="text-sm text-red-200">{message}</p>
        </div>
      )}

      {status === 'ready' && customers.length === 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="text-slate-300">Henüz müşteri eklenmemiş.</p>
        </div>
      )}

      {status === 'ready' && customers.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {customers.map((customer) => (
            <div key={customer.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg">
              <h2 className="text-xl font-semibold">{customer.name}</h2>
              <p className="text-slate-400 text-sm">Email: {customer.email || '—'}</p>
              <p className="text-slate-400 text-sm">Telefon: {customer.phone || '—'}</p>
            </div>
          ))}
        </div>
      )}

      {status === 'loading' && <p className="text-slate-400">Yükleniyor...</p>}
    </main>
  );
}
