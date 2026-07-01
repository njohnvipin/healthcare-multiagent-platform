def check_eligibility(member_id: str = "SARAH-1001") -> dict:
    """Deterministic tool: checks mocked member eligibility and plan status."""
    return {
        "member_id": member_id,
        "member_name": "Sarah M.",
        "plan": "HealthSure Gold 2026",
        "active": True,
        "monthly_premium": 300,
        "deductible": 500,
        "deductible_paid": 200,
        "deductible_remaining": 300,
        "coinsurance_member_percent": 20,
        "coinsurance_plan_percent": 80,
        "out_of_pocket_max": 5000,
    }
