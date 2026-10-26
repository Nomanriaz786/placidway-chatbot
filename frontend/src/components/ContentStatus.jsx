import { Loader2, RefreshCw, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getContentStatus, refreshContent } from '../api.js'

const dateFormat = new Intl.DateTimeFormat(undefined, { day: 'numeric', month: 'short', year: 'numeric' })

// Shows when the content was last updated, and lets an admin re-crawl the pages.
// The admin token is typed in each time and never stored in the browser.
export default function ContentStatus() {
  const [status, setStatus] = useState(null)
  const [open, setOpen] = useState(false)
  const [token, setToken] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    getContentStatus().then(setStatus).catch(() => setStatus(null))
  }, [])

  function close() {
    setOpen(false)
    setToken('')
    setResult(null)
  }

  async function handleRefresh(event) {
    event.preventDefault()
    setBusy(true)
    setResult(null)
    try {
      const stats = await refreshContent(token)
      setResult({ ok: true, text: `Updated: ${stats.pages} pages, ${stats.chunks} passages.` })
      setStatus(await getContentStatus())
    } catch (err) {
      setResult({ ok: false, text: err.message })
    } finally {
      setBusy(false)
      setToken('')
    }
  }

  return (
    <section className="content-status">
      {status && (
        <p>
          Content updated {dateFormat.format(new Date(status.updated_at))}
          <span>{status.pages} pages, {status.passages} passages</span>
        </p>
      )}
      <button type="button" className="refresh-btn" onClick={() => setOpen(true)}>
        <RefreshCw size={15} aria-hidden="true" /> Refresh content
      </button>

      {open && (
        <div className="dialog-backdrop" role="presentation" onClick={close}>
          <form className="dialog" role="dialog" aria-modal="true" aria-labelledby="refresh-title"
            onClick={(e) => e.stopPropagation()} onSubmit={handleRefresh}>
            <div className="dialog-head">
              <h2 id="refresh-title">Refresh content</h2>
              <button type="button" className="icon-btn" onClick={close} aria-label="Close"><X size={18} /></button>
            </div>
            <p>Re-reads the PlacidWay pages and rebuilds the knowledge base. Requires the admin token.</p>
            <label>
              Admin token
              <input type="password" autoComplete="off" required value={token} onChange={(e) => setToken(e.target.value)} disabled={busy} />
            </label>
            {result && <p className={result.ok ? 'dialog-ok' : 'error'}>{result.text}</p>}
            <div className="dialog-actions">
              <button type="button" className="secondary" onClick={close}>Close</button>
              <button type="submit" className="primary" disabled={busy || !token}>
                {busy ? <><Loader2 size={16} className="spin" aria-hidden="true" /> Refreshing</> : 'Refresh'}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  )
}
