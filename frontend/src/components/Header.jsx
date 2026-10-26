import { FileText, MessageSquarePlus, X } from 'lucide-react'
import { QUOTE_URL } from '../config.js'

export default function Header({ infoOpen, onToggleInfo, onNewChat, canReset }) {
  return (
    <header className="navbar">
      <div className="navbar-left">
        <a className="brand" href="https://www.placidway.com" target="_blank" rel="noreferrer" aria-label="PlacidWay home">
          <img src="/placidway-logo.png" alt="PlacidWay" width="112" height="56" />
        </a>
        <span className="badge">AI Assistant</span>
      </div>

      <nav className="navbar-actions" aria-label="Chat actions">
        <button type="button" className="nav-btn" onClick={onNewChat} disabled={!canReset}>
          <MessageSquarePlus size={18} aria-hidden="true" />
          <span className="label">New chat</span>
        </button>
        <button type="button" className="nav-btn pages-toggle" onClick={onToggleInfo} aria-expanded={infoOpen} aria-controls="sidebar">
          {infoOpen ? <X size={18} aria-hidden="true" /> : <FileText size={18} aria-hidden="true" />}
          <span className="label">{infoOpen ? 'Close' : 'Sources'}</span>
        </button>
        <a className="nav-cta" href={QUOTE_URL} target="_blank" rel="noreferrer">Free quote</a>
      </nav>
    </header>
  )
}
