def estimate_mri_cost(mri_charge: float = 1000, deductible_remaining: float = 300, coinsurance_percent: float = 20) -> dict:
    """Deterministic cost calculator. The LLM explains this; it does not calculate it."""
    deductible_payment = min(deductible_remaining, mri_charge)
    remaining_after_deductible = max(mri_charge - deductible_payment, 0)
    member_coinsurance = remaining_after_deductible * (coinsurance_percent / 100)
    plan_payment = remaining_after_deductible - member_coinsurance
    member_total = deductible_payment + member_coinsurance
    return {
        "mri_charge": mri_charge,
        "deductible_payment": deductible_payment,
        "remaining_after_deductible": remaining_after_deductible,
        "member_coinsurance": member_coinsurance,
        "estimated_member_responsibility": member_total,
        "estimated_plan_payment": plan_payment,
        "note": "Estimate assumes prior authorization is approved and provider is in-network.",
    }
