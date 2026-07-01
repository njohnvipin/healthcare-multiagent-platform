from fastapi import FastAPI
from pydantic import BaseModel

from services.ingestion_service import ingest_all_documents
from agents.orchestrator import OrchestratorAgent

app = FastAPI(
    title="Healthcare Multi-Agent AI Platform",
    description="True multi-agent healthcare insurance assistant with Orchestrator + specialized agents.",
    version="1.0.0",
)

orchestrator = OrchestratorAgent()


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "Healthcare Multi-Agent AI Platform is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest-documents")
def ingest_documents():
    return ingest_all_documents()


@app.post("/chat")
def chat(request: ChatRequest):
    return orchestrator.run(request.question)
