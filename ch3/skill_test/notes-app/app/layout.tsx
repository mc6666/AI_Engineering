import type { Metadata } from 'next'
import Link from 'next/link'
import './globals.css'

export const metadata: Metadata = {
  title: { default: 'Notes', template: '%s | Notes' },
  description: 'A simple note-taking app built with Next.js',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav>
          <div className="inner">
            <Link href="/" className="brand">📝 Notes</Link>
            <Link href="/notes/new" className="btn btn-primary">+ New Note</Link>
          </div>
        </nav>
        <main className="container">{children}</main>
      </body>
    </html>
  )
}
