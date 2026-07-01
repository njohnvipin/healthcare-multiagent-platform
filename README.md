# Healthcare Multi-Agent AI Platform

This project is a **true multi-agent healthcare insurance assistant**.

It has:

- Streamlit UI
- FastAPI backend
- Orchestrator Agent
- Policy Agent
- Claims Agent
- Authorization Agent
- Billing Agent
- Separate ChromaDB collections for policy, claims, authorization, and billing knowledge
- Groq LLM integration
- Deterministic tools for eligibility and cost calculation
- OCR-ready service placeholder

## Architecture

```text
User
  ↓
Streamlit UI
  ↓
FastAPI
  ↓
Orchestrator Agent
  ├── Policy Agent → policy_collection → RAG → Groq
  ├── Claims Agent → claims_collection → RAG → Groq
  ├── Authorization Agent → authorization_collection → RAG → Groq
  └── Billing Agent → eligibility_check + billing_calculator → Groq
  ↓
Combined Response
```

## Setup

```bash
python -m venv agentenv
agentenv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add your Groq key in `.env`:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

## Run

Terminal 1:

```bash
python -m uvicorn api:app --reload
```

Terminal 2:

```bash
streamlit run streamlit_app.py
```

Open:

```text
http://localhost:8501
```

First click **Ingest Documents**, then ask:

```text
Is MRI covered, do I need prior authorization, and how much will I pay?
```

## API Docs

Open:

```text
http://localhost:8000/docs
```

Use:

- `POST /ingest-documents`
- `POST /chat`

## Notes

This is a teaching-friendly mini enterprise platform. It does not use real patient data. All data is fictional.
