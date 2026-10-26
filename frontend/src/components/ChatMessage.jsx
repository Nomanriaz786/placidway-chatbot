import { Bot, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { DISCLAIMER, sourceFor } from '../config.js'
import QuoteForm from './QuoteForm.jsx'

// Links in answers open in a new tab; raw HTML from the model is never rendered.
const markdownComponents = {
  a: ({ node, ...props }) => <a {...props} target="_blank" rel="noreferrer" />,
}

export default function ChatMessage({ message, showDisclaimer }) {
  if (message.role === 'user') {
    return (
      <div className="row user">
        <div className="bubble user">{message.content}</div>
      </div>
    )
  }

  return (
    <div className="row bot">
      <div className="avatar" aria-hidden="true"><Bot size={18} /></div>
      <div className="bubble bot">
        <div className="markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
            {message.content}
          </ReactMarkdown>
        </div>

        {message.sources?.length > 0 && (
          <div className="sources">
            <span className="sources-label">Sources</span>
            <ul>
              {message.sources.map((url) => {
                const s = sourceFor(url)
                return (
                  <li key={url}>
                    <a href={url} target="_blank" rel="noreferrer">
                      <span className="kind">{s.kind}</span>
                      <span className="title">{s.title} <ExternalLink size={13} aria-hidden="true" /></span>
                    </a>
                  </li>
                )
              })}
            </ul>
          </div>
        )}

        {showDisclaimer && <p className="disclaimer">{DISCLAIMER}</p>}
        {message.offer_quote && <QuoteForm question={message.question} />}
      </div>
    </div>
  )
}
