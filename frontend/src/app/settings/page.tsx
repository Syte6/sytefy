'use client';

import { useEffect, useState } from 'react';
import { createClient } from '../../lib/api';

const api = createClient();

export default function SettingsPage() {
  const [profile, setProfile] = useState<any>(null);
  const [form, setForm] = useState({ full_name: '', phone: '', business_name: '', business_type: '' });
  const [status, setStatus] = useState<'idle' | 'saving' | 'error' | 'success'>('idle');

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get('/users/me');
        setProfile(data);
        setForm({
          full_name: data.full_name || '',
          phone: data.phone || '',
          business_name: data.business_name || '',
          business_type: data.business_type || '',
        });
      } catch (error) {
        setStatus('error');
      }
    }
    load();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      console.log('Cookies:', document.cookie);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setStatus('saving');
    try {
      const data = await api.put('/users/me', form);
      setProfile(data);
      setStatus('success');
    } catch (error) {
      setStatus('error');
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white p-10 space-y-6">
      <header>
        <p className="text-sm uppercase text-slate-400">Sytefy</p>
        <h1 className="text-3xl font-bold">Profil Ayarları</h1>
        <p className="text-slate-400">Kullanıcı bilgileriniz backend API üzerinden çekilip kaydedilir.</p>
      </header>

      {status === 'error' && <p className="text-red-400">Profil bilgileri alınamadı. Oturum açtığınızdan emin olun.</p>}

      {profile && (
        <form onSubmit={handleSubmit} className="space-y-4 max-w-xl">
          <label className="block">
            <span className="text-sm text-slate-300">Ad Soyad</span>
            <input
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-3"
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
            />
          </label>
          <label className="block">
            <span className="text-sm text-slate-300">Telefon</span>
            <input
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-3"
              name="phone"
              value={form.phone}
              onChange={handleChange}
            />
          </label>
          <label className="block">
            <span className="text-sm text-slate-300">İşletme Adı</span>
            <input
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-3"
              name="business_name"
              value={form.business_name}
              onChange={handleChange}
            />
          </label>
          <label className="block">
            <span className="text-sm text-slate-300">Sektör</span>
            <input
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-3"
              name="business_type"
              value={form.business_type}
              onChange={handleChange}
            />
          </label>
          <button
            type="submit"
            className="rounded-lg bg-indigo-500 px-6 py-3 font-semibold text-white"
            disabled={status === 'saving'}
          >
            {status === 'saving' ? 'Kaydediliyor...' : 'Kaydet'}
          </button>
          {status === 'success' && <p className="text-green-400">Profil güncellendi.</p>}
        </form>
      )}

      {status === 'idle' && !profile && <p className="text-slate-400">Profil yükleniyor...</p>}
    </main>
  );
}
