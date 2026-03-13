from __future__ import annotations

import json
import os
from typing import Any

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="AutoResearch", page_icon=":mag:", layout="wide")
st.title("AutoResearch")
st.caption("Multi-agent research assistant powered by LangGraph and FastAPI.")


def stream_events(query: str):
    with httpx.stream(
        "GET",
        f"{BACKEND_BASE_URL}/research/stream",
        params={"query": query},
        timeout=120.0,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line or not line.startswith("data: "):
                continue
            yield json.loads(line[6:])


query = st.text_input(
    "Enter your research question",
    placeholder="What are the latest enterprise use cases for small language models?",
)

run_col, api_col = st.columns([3, 1])
with api_col:
    st.text_input("Backend URL", value=BACKEND_BASE_URL, disabled=True)

if run_col.button("Research", type="primary", use_container_width=True) and query:
    status_box = st.status("Running research workflow", expanded=True)
    progress_placeholder = st.empty()
    report_placeholder = st.empty()
    sidebar = st.sidebar
    sidebar.empty()
    latest_payload: dict[str, Any] = {}

    try:
        for event in stream_events(query):
            latest_payload = event.get("payload", {})
            if event["event"] == "node_complete":
                status_box.write(f"{event['node']} completed")
                progress_placeholder.json(
                    {
                        "current_step": event["current_step"],
                        "sub_topics": latest_payload.get("sub_topics", []),
                        "contradictions": latest_payload.get("contradictions", []),
                    }
                )
            elif event["event"] == "completed":
                status_box.update(label="Research complete", state="complete", expanded=False)
                report_placeholder.markdown(latest_payload.get("final_report", ""))
                sidebar.subheader("Sub-topics")
                sidebar.write(latest_payload.get("sub_topics", []))
                sidebar.subheader("Contradictions")
                sidebar.write(latest_payload.get("contradictions", []))
                sidebar.subheader("References")
                sidebar.write(latest_payload.get("references", []))
    except httpx.HTTPError as exc:
        status_box.update(label="Research failed", state="error", expanded=True)
        st.error(f"Backend request failed: {exc}")
