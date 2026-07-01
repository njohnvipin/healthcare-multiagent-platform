from services.llm_service import safe_llm_response
from tools.eligibility_check import check_eligibility
from tools.billing_calculator import estimate_mri_cost


class BillingAgent:
    name = "Billing Agent"

    def run(self, question: str) -> dict:
        eligibility = check_eligibility()
        estimate = estimate_mri_cost(
            mri_charge=1000,
            deductible_remaining=eligibility["deductible_remaining"],
            coinsurance_percent=eligibility["coinsurance_member_percent"],
        )
        fallback = (
            f"Billing Agent: Sarah has ${eligibility['deductible_remaining']} deductible remaining. "
            f"For a $1000 MRI, estimated member responsibility is ${estimate['estimated_member_responsibility']:.2f}, "
            f"and estimated plan payment is ${estimate['estimated_plan_payment']:.2f}."
        )
        prompt = f"""
You are the Billing Agent for a healthcare insurance AI platform.
Use the deterministic eligibility and cost calculation JSON below. Do not recalculate incorrectly.
Explain the estimate in simple language.

Eligibility JSON:
{eligibility}

Cost Estimate JSON:
{estimate}

User Question:
{question}

Billing Agent Answer:
"""
        answer = safe_llm_response(prompt, fallback)
        return {"agent": self.name, "answer": answer, "sources": [{"source": "eligibility_check + billing_calculator", "doc_type": "tool"}]}
