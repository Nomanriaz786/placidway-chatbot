async function postJSON(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Something went wrong. Please try again.')
  }
  return data
}

export const askQuestion = (messages) => postJSON('/api/chat', { messages })
export const submitLead = (lead) => postJSON('/api/lead', lead)
