'use client';

import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createClient } from '../../lib/api';

type Invoice = {
  id: number;
  number: string;
  title: string;
  description?: string | null;
  amount: number;
  currency: string;
  status: string;
  due_date: string;
  issued_at: string;
};

type CreateInvoiceForm = {
  title: string;
  amount: string;
  currency: string;
  dueDate: string;
  description: string;
};

const client = createClient();
const statusLabels: Record<string, string> = {
  draft: 'Taslak',
  sent: 'Gönderildi',
  paid: 'Ödendi',
  void: 'Geçersiz',
};

function formatDate(value: string) {
  const date = new Date(value);
  return new Intl.DateTimeFormat('tr-TR', { dateStyle: 'medium' }).format(date);
}

export default function FinancesPage() {
  const queryClient = useQueryClient();
  const [formState, setFormState] = useState<CreateInvoiceForm>({
    title: '',
    amount: '',
    currency: 'TRY',
    dueDate: '',
    description: '',
  });
  const [formMessage, setFormMessage] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => client.get<Invoice[]>('/finances/invoices/'),
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      if (!formState.dueDate) {
        throw new Error('Vade tarihi zorunlu.');
      }
      const payload = {
        title: formState.title,
        amount: parseFloat(formState.amount),
        currency: formState.currency,
        due_date: new Date(formState.dueDate).toISOString(),
        description: formState.description || undefined,
      };
      await client.post('/finances/invoices/', payload);
    },
    onSuccess: () => {
      setFormMessage('Fatura oluşturuldu.');
      setFormState({ title: '', amount: '', currency: 'TRY', dueDate: '', description: '' });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
    },
    onError: (err) => setFormMessage(err instanceof Error ? err.message : 'Fatura oluşturulamadı.'),
  });

  const markPaidMutation = useMutation({
    mutationFn: (id: number) => client.put(`/finances/invoices/${id}`, { status: 'paid' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['invoices'] }),
  });

  const invoices = useMemo(() => data ?? [], [data]);

  return (
    <main className="min-h-screen bg-slate-950 text-white p-10 space-y-8">
      <header className="space-y-2">
        <p className="text-sm uppercase text-slate-400">Sytefy</p>
        <h1 className="text-3xl font-bold">Faturalar</h1>
        <p className="text-slate-400">Gelirlerinizi takip edin, fatura durumlarını güncelleyin.</p>
      </header>

      <section className="grid gap-6 md:grid-cols-2">
        <form
          className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            createMutation.mutate();
          }}
        >
          <h2 className="text-lg font-semibold">Yeni Fatura</h2>
          <div>
            <label className="text-sm text-slate-400 block mb-1">Başlık</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
              value={formState.title}
              onChange={(e) => setFormState((prev) => ({ ...prev, title: e.target.value }))}
              required
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-slate-400 block mb-1">Tutar</label>
              <input
                type="number"
                step="0.01"
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
                value={formState.amount}
                onChange={(e) => setFormState((prev) => ({ ...prev, amount: e.target.value }))}
                required
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 block mb-1">Para Birimi</label>
              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
                value={formState.currency}
                onChange={(e) => setFormState((prev) => ({ ...prev, currency: e.target.value }))}
              />
            </div>
          </div>
          <div>
            <label className="text-sm text-slate-400 block mb-1">Vade Tarihi</label>
            <input
              type="date"
              className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
              value={formState.dueDate}
              onChange={(e) => setFormState((prev) => ({ ...prev, dueDate: e.target.value }))}
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
          {formMessage && <p className="text-sm text-slate-300">{formMessage}</p>}
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="w-full rounded-lg bg-emerald-600 py-2 font-semibold hover:bg-emerald-500 disabled:opacity-50"
          >
            {createMutation.isPending ? 'Kaydediliyor...' : 'Fatura Oluştur'}
          </button>
        </form>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-3">
          <h2 className="text-xl font-semibold">Durumlara Göre Filtre</h2>
          <p className="text-sm text-slate-400">Yakında durum bazlı raporlar burada olacak.</p>
        </section>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Fatura Listesi</h2>
        {isLoading && <p className="text-slate-400">Yükleniyor...</p>}
        {error && <p className="text-red-400">{error instanceof Error ? error.message : 'Veri alınamadı.'}</p>}
        {!isLoading && !error && invoices.length === 0 && (
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-slate-300">Henüz fatura yok.</div>
        )}
        <div className="grid gap-4">
          {invoices.map((invoice) => (
            <div key={invoice.id} className="rounded-xl border border-slate-800 bg-slate-900/80 p-6 space-y-3">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-slate-400">{invoice.number}</p>
                  <h3 className="text-xl font-semibold">{invoice.title}</h3>
                  <p className="text-sm text-slate-400">
                    {statusLabels[invoice.status] ?? invoice.status} · Vade {formatDate(invoice.due_date)} · {invoice.amount.toFixed(2)}{' '}
                    {invoice.currency}
                  </p>
                </div>
                <div className="flex gap-2">
                  {invoice.status != 'paid' && (
                    <button
                      className="rounded-lg border border-emerald-500 px-3 py-1 text-sm hover:bg-emerald-500/10"
                      disabled={markPaidMutation.isPending}
                      onClick={() => markPaidMutation.mutate(invoice.id)}
                    >
                      Ödendi İşaretle
                    </button>
                  )}
                </div>
              </div>
              {invoice.description && <p className="text-slate-300">{invoice.description}</p>}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
