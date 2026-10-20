import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="empty">
      <h2>Note not found</h2>
      <p>The note you are looking for does not exist or was deleted.</p>
      <br />
      <Link href="/" className="btn btn-primary">← Back to Notes</Link>
    </div>
  )
}
