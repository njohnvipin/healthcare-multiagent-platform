from services.vector_store import ingest_folder


def ingest_all_documents() -> dict:
    counts = {
        "policy_chunks": ingest_folder("policy_collection", "data/policies", "policy"),
        "claims_chunks": ingest_folder("claims_collection", "data/claims", "claims"),
        "authorization_chunks": ingest_folder("authorization_collection", "data/authorizations", "authorization"),
        "billing_chunks": ingest_folder("billing_collection", "data/billing", "billing"),
    }
    return {"status": "success", "message": "Documents ingested into separate agent collections", "counts": counts}
