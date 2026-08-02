const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function handleResponse(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed with status ${res.status}`)
  }
  return res.json()
}

export const api = {
  extractFromText: (text) =>
    fetch(`${BASE_URL}/api/complaints/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }).then(handleResponse),

  extractFromFile: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return fetch(`${BASE_URL}/api/complaints/extract-file`, {
      method: 'POST',
      body: formData,
    }).then(handleResponse)
  },

  saveComplaint: (complaint) =>
    fetch(`${BASE_URL}/api/complaints`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(complaint),
    }).then(handleResponse),

  chat: (message, complaintId) =>
    fetch(`${BASE_URL}/api/complaints/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, complaint_id: complaintId || null }),
    }).then(handleResponse),
}
