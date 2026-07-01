from services.vector_store import query_collection, format_results


def authorization_lookup(question: str) -> dict:
    results = query_collection("authorization_collection", question, n_results=3)
    return format_results(results)
