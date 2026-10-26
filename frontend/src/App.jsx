import { Bot } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { askQuestion } from './api.js'
import ChatMessage from './components/ChatMessage.jsx'
import Composer from './components/Composer.jsx'
import Header from './components/Header.jsx'
import Sidebar from './components/Sidebar.jsx'
import { HISTORY_LIMIT, SUGGESTIONS } from './config.js'

export default function App() {
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [infoOpen, setInfoOpen] = useState(false)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, busy])

  // The disclaimer appears once: on the first answer that touches a medical topic.
  const disclaimerIndex = messages.findIndex((m) => m.role === 'assistant' && m.medical_topic)

  function startNewChat() {
    setMessages([])
    setDraft('')
    setError('')
  }

  async function send(text) {
    const question = text.trim()
    if (!question || busy) return
    const next = [...messages, { role: 'user', content: question }]
    setMessages(next)
    setDraft('')
    setError('')
    setInfoOpen(false)
    setBusy(true)
    try {
      const history = next.slice(-HISTORY_LIMIT).map(({ role, content }) => ({ role, content }))
      const reply = await askQuestion(history)
      setMessages([...next, { role: 'assistant', content: reply.answer, ...reply, question }])
    } catch (err) {
      setError(err.message)
      setMessages(messages)
      setDraft(question)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="app">
      <Header
        infoOpen={infoOpen}
        onToggleInfo={() => setInfoOpen((open) => !open)}
        onNewChat={startNewChat}
        canReset={messages.length > 0 && !busy}
      />
      <div className="layout">
        <Sidebar open={infoOpen} onAsk={send} busy={busy} />
        <main className="chat">
          <div className="messages" aria-live="polite">
            {messages.length === 0 && (
              <section className="welcome">
                <h1>Ask about alternative cancer treatment at ITC Tijuana</h1>
                <p>Prices, what each package includes, and how the programs work. Every answer links to the PlacidWay page it came from.</p>
                <div className="suggestions inline">
                  {SUGGESTIONS.slice(0, 3).map((s) => (
                    <button type="button" key={s} onClick={() => send(s)}>{s}</button>
                  ))}
                </div>
              </section>
            )}
            {messages.map((m, i) => (
              <ChatMessage key={i} message={m} showDisclaimer={i === disclaimerIndex} />
            ))}
            {busy && (
              <div className="row bot">
                <div className="avatar" aria-hidden="true"><Bot size={18} /></div>
                <div className="bubble bot typing"><span /><span /><span /> Thinking…</div>
              </div>
            )}
            <div ref={endRef} />
          </div>
          {error && <p className="error banner" role="alert">{error}</p>}
          <Composer onSend={send} busy={busy} draft={draft} onDraftChange={setDraft} />
          <p className="footnote">Built by Muhammad Noman Riaz</p>
        </main>
      </div>
    </div>
  )
}
