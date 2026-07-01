from services.llm_service import safe_llm_response
from tools.claim_lookup import claim_lookup


class ClaimsAgent:
    name = "Claims Agent"

    def run(self, question: str) -> dict:
        retrieved = claim_lookup(question)
        context = retrieved["context"]
        fallback = (
            "Claims Agent: Sarah's MRI claim CLM-8892 was denied because prior authorization was missing. "
            "Denial code: PA_MISSING."
        )
        prompt = f"""
You are the Claims Agent for a healthcare insurance AI platform.
Answer ONLY using the claims context below. Explain claim status, denial reasons, and EOB details clearly.
Return a concise answer with bullet points and mention sources.

Claims Context:
{context}

User Question:
{question}

Claims Agent Answer:
"""
        answer = safe_llm_response(prompt, fallback)
        return {"agent": self.name, "answer": answer, "sources": retrieved["sources"]}
