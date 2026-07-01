from services.llm_service import safe_llm_response
from tools.authorization_lookup import authorization_lookup


class AuthorizationAgent:
    name = "Authorization Agent"

    def run(self, question: str) -> dict:
        retrieved = authorization_lookup(question)
        context = retrieved["context"]
        fallback = (
            "Authorization Agent: MRI scans require prior authorization when performed as outpatient advanced imaging. "
            "Medical necessity documentation and physician notes are required."
        )
        prompt = f"""
You are the Authorization Agent for a healthcare insurance AI platform.
Answer ONLY using the authorization context below. Focus on prior authorization, medical necessity, approval rules, and missing authorization.
Return a concise answer with bullet points and mention sources.

Authorization Context:
{context}

User Question:
{question}

Authorization Agent Answer:
"""
        answer = safe_llm_response(prompt, fallback)
        return {"agent": self.name, "answer": answer, "sources": retrieved["sources"]}
