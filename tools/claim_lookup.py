from services.vector_store import query_collection, format_results


def claim_lookup(question: str) -> dict:
    results = query_collection("claims_collection", question, n_results=3)
    return format_results(results)
