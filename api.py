from fastapi import FastAPI
from pydantic import BaseModel

from services.ingestion_service import (
    ingest_all_documents,
    process_uploaded_documents,
    process_and_ingest_documents,
)
from agents.langgraph_orchestrator import (
    LangGraphHealthcareOrchestrator,
)
app = FastAPI(
    title="Healthcare Multi-Agent AI Platform",
    description="The multi-agent healthcare insurance assistant with Orchestrator + specialized agents.",
    version="1.0.0",
)

orchestrator = LangGraphHealthcareOrchestrator()

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

@app.post("/process-documents")
def process_documents():
    return process_uploaded_documents()

@app.post("/process-and-ingest")
def process_and_ingest():
    return process_and_ingest_documents()

@app.post("/chat")
def chat(request: ChatRequest):
    return orchestrator.run(request.question)
