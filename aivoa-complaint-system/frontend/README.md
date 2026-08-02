# AIVOA Complaint Management System — Frontend

React + Redux Toolkit UI matching the reference "Log Customer Complaint" / "AI Complaint Intake Assistant" layout.

## Setup

```bash
cd frontend
npm install
cp .env.example .env
# edit .env if your backend isn't on localhost:8000 (e.g. your Codespaces backend URL)
npm run dev
```

Opens on `http://localhost:5173`.

## How it's wired to the backend

- `src/api/client.js` — thin fetch wrapper for the 4 backend calls (extract from text, extract from
  file, save, chat)
- `src/store/complaintSlice.js` — Redux Toolkit slice holding the form fields, extraction state
  (loading/succeeded/failed), and chat history, with `createAsyncThunk`s calling the API
- `src/components/ComplaintForm.jsx` — the left panel, four numbered sections matching the reference
  screenshot exactly (Origin & Customer / Product & Batch / Complaint Details / Assessment & Priority).
  Fields turn teal-tinted when they were populated by the AI extraction, so a reviewer can see at a
  glance what the AI filled vs what's manually entered.
- `src/components/AICopilotPanel.jsx` — the right panel: drag-and-drop upload, paste-text box,
  extraction progress, AI insight cards (completeness score, risk classification, summary, duplicate
  warning), and the chat copilot at the bottom

## Note on the Codespaces backend URL

If your backend is running in GitHub Codespaces (a `*.app.github.dev` URL) rather than `localhost`,
set `VITE_API_BASE_URL` in `.env` to that forwarded URL, and make sure the backend port's visibility
is set to **Public** in the Codespaces "Ports" tab — otherwise the browser's fetch calls will be
blocked by Codespaces' auth layer.
