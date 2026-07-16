import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Healthcare Multi-Agent AI", page_icon="🏥", layout="wide")
st.title("🏥 Healthcare Multi-Agent AI Platform")
st.caption("Orchestrator Agent + Policy Agent + Claims Agent + Authorization Agent + Billing Agent")

with st.sidebar:
    st.header("IDP and RAG Controls")

    if st.button("1. Process Documents with OCR"):
        with st.spinner(
            "Reading images and PDFs and extracting text..."
        ):
            try:
                response = requests.post(
                    f"{API_URL}/process-documents",
                    timeout=300,
                )
                response.raise_for_status()

                result = response.json()

                if result.get("failed_count", 0) > 0:
                    st.warning(
                        "OCR completed with some failures."
                    )
                else:
                    st.success(
                        "OCR processing completed successfully."
                    )

                st.json(result)

            except Exception as exc:
                st.error(
                    f"Could not process documents: {exc}"
                )

    if st.button("2. Ingest Processed Documents"):
        with st.spinner(
            "Creating chunks, embeddings, and "
            "storing them in ChromaDB..."
        ):
            try:
                response = requests.post(
                    f"{API_URL}/ingest-documents",
                    timeout=300,
                )
                response.raise_for_status()

                st.success(
                    "Processed documents ingested successfully."
                )
                st.json(response.json())

            except Exception as exc:
                st.error(
                    f"Could not ingest documents: {exc}"
                )

    if st.button("Run Full OCR → RAG Pipeline"):
        with st.spinner(
            "Running OCR, chunking, embeddings, "
            "and vector ingestion..."
        ):
            try:
                response = requests.post(
                    f"{API_URL}/process-and-ingest",
                    timeout=600,
                )
                response.raise_for_status()

                st.success(
                    "Complete IDP and RAG pipeline finished."
                )
                st.json(response.json())

            except Exception as exc:
                st.error(
                    f"Pipeline failed: {exc}"
                )

    st.markdown("### Sample Questions")
    st.code("Is MRI covered?")
    st.code("Do I need prior authorization for MRI?")
    st.code("Why was Sarah's MRI claim denied?")
    st.code(
        "Is MRI covered, do I need prior authorization, "
        "and how much will I pay?"
    )
question = st.text_area("Ask Sarah's healthcare insurance question", value="Is MRI covered, do I need prior authorization, and how much will I pay?", height=100)

if st.button("Ask Multi-Agent Platform") and question.strip():
    with st.spinner("Orchestrator is routing the request to specialist agents..."):
        try:
            response = requests.post(f"{API_URL}/chat", json={"question": question}, timeout=120)
            data = response.json()
        except Exception as exc:
            st.error(f"Could not connect to FastAPI: {exc}")
            st.stop()

    st.subheader("Final Combined Answer")
    st.write(data.get("answer", ""))

    st.subheader("Orchestrator Routing")
    st.write(data.get("routed_to", []))

    st.subheader("Specialist Agent Outputs")
    for result in data.get("agent_results", []):
        with st.expander(result.get("agent", "Agent")):
            st.write(result.get("answer", ""))
            st.caption("Sources")
            st.json(result.get("sources", []))

    st.subheader("All Sources")
    st.json(data.get("sources", []))
