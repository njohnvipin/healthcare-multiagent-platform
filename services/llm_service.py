from langchain_groq import ChatGroq
from config import GROQ_API_KEY, GROQ_MODEL


def get_llm(temperature: float = 0.2):
    if not GROQ_API_KEY:
        return None
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=temperature,
    )


def safe_llm_response(prompt: str, fallback: str) -> str:
    llm = get_llm()
    if llm is None:
        return fallback
    try:
        return llm.invoke(prompt).content
    except Exception as exc:
        return f"{fallback}\n\n[LLM unavailable or failed: {exc}]"
