from services.llm_service import safe_llm_response
from tools.policy_lookup import policy_lookup


class PolicyAgent:
    name = "Policy Agent"

    def run(self, question: str) -> dict:
        retrieved = policy_lookup(question)
        context = retrieved["context"]
        fallback = (
            "Policy Agent: Based on the policy documents, MRI scans are covered when medically necessary "
            "and ordered by an in-network provider. Coverage is subject to deductible and 20% member coinsurance."
        )
        prompt = f"""
You are the Policy Agent for a healthcare insurance AI platform.
Answer ONLY using the policy context below. If information is missing, say it is not available in policy context.
Return a concise answer with bullet points and mention sources.

Policy Context:
{context}

User Question:
{question}

Policy Agent Answer:
"""
        answer = safe_llm_response(prompt, fallback)
        return {"agent": self.name, "answer": answer, "sources": retrieved["sources"]}
