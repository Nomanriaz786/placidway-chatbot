import { ExternalLink, MessageCircleQuestion, ShieldCheck } from 'lucide-react'
import { SOURCES, SUGGESTIONS } from '../config.js'

const RULES = [
  'Uses only the PlacidWay pages listed below.',
  'Links every answer to the page it came from.',
  "Says so when a page doesn't cover your question, instead of guessing a price.",
]

export default function Sidebar({ open, onAsk, busy }) {
  return (
    <aside id="sidebar" className={`sidebar${open ? ' open' : ''}`}>
      <section>
        <h2><ShieldCheck size={16} aria-hidden="true" /> How it answers</h2>
        <ul className="rules">
          {RULES.map((rule) => <li key={rule}>{rule}</li>)}
        </ul>
      </section>

      <section>
        <h2><MessageCircleQuestion size={16} aria-hidden="true" /> Try asking</h2>
        <div className="suggestions">
          {SUGGESTIONS.map((s) => (
            <button type="button" key={s} disabled={busy} onClick={() => onAsk(s)}>{s}</button>
          ))}
        </div>
      </section>

      <section>
        <h2><ExternalLink size={16} aria-hidden="true" /> Pages it knows</h2>
        <ul className="page-list">
          {SOURCES.map((s) => (
            <li key={s.url}>
              <a href={s.url} target="_blank" rel="noreferrer">
                <span className="kind">{s.kind}</span>
                {s.title}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </aside>
  )
}
