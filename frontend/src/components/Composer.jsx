import { SendHorizontal } from 'lucide-react'
import { useEffect, useRef } from 'react'

const MAX_HEIGHT = 160

export default function Composer({ onSend, busy, draft, onDraftChange }) {
  const inputRef = useRef(null)

  // Grow with the text up to MAX_HEIGHT, then scroll.
  useEffect(() => {
    const el = inputRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, MAX_HEIGHT)}px`
  }, [draft])

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      onSend(draft)
    }
  }

  return (
    <form className="composer" onSubmit={(e) => { e.preventDefault(); onSend(draft) }}>
      <label htmlFor="question" className="sr-only">Your question</label>
      <textarea
        id="question"
        ref={inputRef}
        rows={1}
        value={draft}
        maxLength={1000}
        placeholder="Ask about a treatment, package or price…"
        onChange={(e) => onDraftChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={busy}
      />
      <button type="submit" className="send-btn" disabled={busy || !draft.trim()} aria-label="Send question">
        <SendHorizontal size={20} aria-hidden="true" />
      </button>
    </form>
  )
}
