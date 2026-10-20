import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Photo Organizer',
  description: 'Organize your photos into albums',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50">
        <header className="bg-white border-b border-slate-200 px-6 py-4">
          <h1 className="text-xl font-semibold text-slate-800">Photo Organizer</h1>
        </header>
        <main className="px-6 py-8 max-w-7xl mx-auto">{children}</main>
      </body>
    </html>
  );
}
