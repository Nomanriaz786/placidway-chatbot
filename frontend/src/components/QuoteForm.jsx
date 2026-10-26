import { useState } from 'react'
import { submitLead } from '../api.js'
import { QUOTE_URL } from '../config.js'

export default function QuoteForm({ question }) {
  const [step, setStep] = useState('offer')
  const [form, setForm] = useState({ name: '', email: '' })
  const [error, setError] = useState('')

  if (step === 'sent') {
    return <p className="lead-done">Thanks, {form.name}. PlacidWay's team will contact you at {form.email}.</p>
  }

  if (step === 'offer') {
    return (
      <div className="quote-actions">
        <button type="button" className="secondary" onClick={() => setStep('form')}>Leave my details for a free quote</button>
        <a href={QUOTE_URL} target="_blank" rel="noreferrer">Open PlacidWay's quote form</a>
      </div>
    )
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    try {
      await submitLead({ ...form, question })
      setStep('sent')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form className="lead-form" onSubmit={handleSubmit}>
      <label>
        Name
        <input required maxLength={100} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
      </label>
      <label>
        Email
        <input required type="email" maxLength={200} value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
      </label>
      <button type="submit" className="primary">Send</button>
      {error && <p className="error">{error}</p>}
    </form>
  )
}
