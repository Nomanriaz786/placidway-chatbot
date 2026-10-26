async function request(path, { method = 'GET', body, headers = {} } = {}) {
  const res = await fetch(path, {
    method,
    headers: body ? { 'Content-Type': 'application/json', ...headers } : headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Something went wrong. Please try again.')
  }
  return data
}

export const askQuestion = (messages) => request('/api/chat', { method: 'POST', body: { messages } })
export const submitLead = (lead) => request('/api/lead', { method: 'POST', body: lead })
export const getContentStatus = () => request('/api/status')
export const refreshContent = () => request('/api/refresh', { method: 'POST' })
