from services.vector_store import query_collection, format_results


def policy_lookup(question: str) -> dict:
    results = query_collection("policy_collection", question, n_results=3)
    return format_results(results)
