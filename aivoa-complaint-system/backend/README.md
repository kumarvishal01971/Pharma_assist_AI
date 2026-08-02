# AIVOA Complaint Management System — Backend

FastAPI + LangGraph + Groq backend for the AI-powered pharmaceutical complaint intake assignment.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your GROQ_API_KEY (get one at https://console.groq.com)
```

### Database

You need a running MySQL instance. Easiest local option:

```bash
docker run --name aivoa-mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=aivoa_complaints -p 3306:3306 -d mysql:8.0
```

Give it about 20-30 seconds to finish initializing before starting the backend.

Tables are auto-created on app startup (see `app/main.py`) — no manual migration needed for this assignment.

### Run

```bash
uvicorn app.main:app --reload --port 8000
```

API docs (Swagger) will be at `http://localhost:8000/docs`.

## How the AI pipeline works

`app/agents/graph.py` builds a LangGraph `StateGraph` with four sequential nodes:

1. **extract_fields** — calls Groq `gemma2-9b-it` with a strict JSON-extraction prompt to pull structured
   fields (product, batch, dates, severity, etc.) out of raw complaint text.
2. **check_completeness** — flags which required fields are missing (bonus feature: Complaint Completeness Checker).
3. **classify_risk** — calls Groq `llama-3.3-70b-versatile` (stronger reasoning model) to assign a risk level
   with rationale, informed by ICH Q9-style thinking (bonus feature: AI Risk Classification).
4. **summarize** — produces a 2-3 sentence QA-reviewer summary (bonus feature: Complaint Summary).

Duplicate detection (`app/agents/duplicate.py`) runs as a plain DB query rather than an LLM call — it checks
existing complaints for matching `batch_lot_number` + `product_name`. This is intentionally simple (matches
the assignment's "production-grade OCR/parsing not required" spirit) but the docstring notes how you'd extend
it with embedding similarity for a production version.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/complaints/extract` | Extract fields from pasted text |
| POST | `/api/complaints/extract-file` | Extract fields from an uploaded PDF/DOCX/TXT/EML |
| POST | `/api/complaints` | Save a (reviewed) complaint to the DB |
| GET | `/api/complaints` | List all complaints |
| GET | `/api/complaints/{id}` | Get one complaint |
| PUT | `/api/complaints/{id}` | Update a complaint |
| POST | `/api/complaints/chat` | AI Copilot chat, grounded in a complaint's data |

## Sample test payload

```bash
curl -X POST http://localhost:8000/api/complaints/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "From: qa@pharmadist.com\nSubject: Complaint - Batch B4521\n\nWe received Batch B4521 of Amoxicillin 500mg capsules and noticed visible discoloration in about 12kg of the shipment. Manufacturing date was 2025-11-01, expiry 2027-11-01. This is a critical quality concern given the batch may still be in circulation. Please investigate urgently."}'
```
