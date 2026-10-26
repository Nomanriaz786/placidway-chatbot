import { Loader2, RefreshCw } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getContentStatus, refreshContent } from '../api.js'

const dateFormat = new Intl.DateTimeFormat(undefined, { day: 'numeric', month: 'short', year: 'numeric' })

// Shows when the content was last updated and lets anyone re-crawl the pages.
// The server allows one refresh attempt every few minutes for the whole site.
export default function ContentStatus() {
  const [status, setStatus] = useState(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    getContentStatus().then(setStatus).catch(() => setStatus(null))
  }, [])

  async function handleRefresh() {
    setBusy(true)
    setResult(null)
    try {
      const stats = await refreshContent()
      setResult({ ok: true, text: `Updated: ${stats.pages} pages, ${stats.chunks} passages.` })
      setStatus(await getContentStatus())
    } catch (err) {
      setResult({ ok: false, text: err.message })
    } finally {
      setBusy(false)
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
      <button type="button" className="refresh-btn" onClick={handleRefresh} disabled={busy}>
        {busy
          ? <><Loader2 size={15} className="spin" aria-hidden="true" /> Refreshing…</>
          : <><RefreshCw size={15} aria-hidden="true" /> Refresh content</>}
      </button>
      {result && <p className={result.ok ? 'refresh-ok' : 'refresh-error'} role="status">{result.text}</p>}
    </section>
  )
}
