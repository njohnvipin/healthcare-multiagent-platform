import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Healthcare Multi-Agent AI", page_icon="🏥", layout="wide")
st.title("🏥 Healthcare Multi-Agent AI Platform")
st.caption("Orchestrator Agent + Policy Agent + Claims Agent + Authorization Agent + Billing Agent")

with st.sidebar:
    st.header("System Controls")
    if st.button("Ingest Documents"):
        with st.spinner("Ingesting policy, claims, authorization, and billing documents..."):
            try:
                response = requests.post(f"{API_URL}/ingest-documents", timeout=120)
                st.success(response.json())
            except Exception as exc:
                st.error(f"Could not connect to FastAPI: {exc}")

    st.markdown("### Sample Questions")
    st.code("Is MRI covered?")
    st.code("Do I need prior authorization for MRI?")
    st.code("Why was my MRI claim denied?")
    st.code("Is MRI covered, do I need prior authorization, and how much will I pay?")

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
