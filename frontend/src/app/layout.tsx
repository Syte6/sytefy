import type { Metadata } from 'next';
import Link from 'next/link';
import '../styles/globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'Sytefy Console',
  description: 'Güvenli dijital sekreter platformu',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body className="bg-slate-950 text-white">
        <Providers>
          <div className="min-h-screen flex flex-col">
            <header className="border-b border-slate-800 bg-slate-900/60">
              <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
                <div className="space-y-1">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Sytefy</p>
                  <span className="text-lg font-semibold">Dijital Sekreter</span>
                </div>
                <nav className="flex items-center gap-4 text-sm font-medium text-slate-300">
                  <Link href="/" className="hover:text-white transition-colors">
                    Sağlık
                  </Link>
                  <Link href="/appointments" className="hover:text-white transition-colors">
                    Randevular
                  </Link>
                  <Link href="/finances" className="hover:text-white transition-colors">
                    Finans
                  </Link>
                  <Link href="/notifications" className="hover:text-white transition-colors">
                    Bildirimler
                  </Link>
                  <Link href="/customers" className="hover:text-white transition-colors">
                    Müşteriler
                  </Link>
                  <Link href="/settings" className="hover:text-white transition-colors">
                    Ayarlar
                  </Link>
                </nav>
              </div>
            </header>
            <div className="flex-1">{children}</div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
