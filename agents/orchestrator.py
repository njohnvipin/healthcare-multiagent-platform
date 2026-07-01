from typing import List

from services.llm_service import safe_llm_response
from agents.policy_agent import PolicyAgent
from agents.claims_agent import ClaimsAgent
from agents.authorization_agent import AuthorizationAgent
from agents.billing_agent import BillingAgent


class OrchestratorAgent:
    """Routes questions to specialized agents and combines their outputs."""

    def __init__(self):
        self.policy_agent = PolicyAgent()
        self.claims_agent = ClaimsAgent()
        self.authorization_agent = AuthorizationAgent()
        self.billing_agent = BillingAgent()

    def detect_intents(self, question: str) -> List[str]:
        q = question.lower()
        intents = []

        policy_terms = ["covered", "coverage", "policy", "benefit", "deductible", "coinsurance", "excluded", "mri"]
        claims_terms = ["claim", "denied", "denial", "eob", "status", "paid", "appeal"]
        auth_terms = ["prior authorization", "authorization", "approval", "medical necessity", "preauth", "pa"]
        billing_terms = ["pay", "cost", "owe", "responsibility", "premium", "out-of-pocket", "out of pocket", "deductible", "coinsurance"]

        if any(t in q for t in policy_terms):
            intents.append("policy")
        if any(t in q for t in claims_terms):
            intents.append("claims")
        if any(t in q for t in auth_terms):
            intents.append("authorization")
        if any(t in q for t in billing_terms):
            intents.append("billing")

        if not intents:
            intents = ["policy"]
        return list(dict.fromkeys(intents))

    def run(self, question: str) -> dict:
        intents = self.detect_intents(question)
        agent_results = []

        if "policy" in intents:
            agent_results.append(self.policy_agent.run(question))
        if "claims" in intents:
            agent_results.append(self.claims_agent.run(question))
        if "authorization" in intents:
            agent_results.append(self.authorization_agent.run(question))
        if "billing" in intents:
            agent_results.append(self.billing_agent.run(question))

        combined = "\n\n".join([f"{r['agent']}:\n{r['answer']}" for r in agent_results])
        fallback = combined
        prompt = f"""
You are the Orchestrator Agent for a healthcare insurance multi-agent platform.
Your job is to combine specialist agent outputs into one clear final answer.
Do not add facts that are not present in the specialist outputs.
Use sections: Coverage, Prior Authorization, Claims, Cost Estimate, Next Steps when relevant.

User Question:
{question}

Specialist Agent Outputs:
{combined}

Final Combined Answer:
"""
        final_answer = safe_llm_response(prompt, fallback)

        sources = []
        for result in agent_results:
            sources.extend(result.get("sources", []))

        return {
            "question": question,
            "routed_to": intents,
            "agent_results": agent_results,
            "answer": final_answer,
            "sources": sources,
        }
