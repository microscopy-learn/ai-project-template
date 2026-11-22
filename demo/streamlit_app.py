"""Streamlit demo for the project.

Deploy on Streamlit Community Cloud with `demo/streamlit_app.py` as the entry point.

Run locally: uv run --extra demo streamlit run demo/streamlit_app.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st  # noqa: E402

from app.pipeline import get_pipeline  # noqa: E402

st.set_page_config(page_title="AI Project demo", page_icon=":mag:")
st.title("AI Project demo")
st.caption("Replace this caption with the one-line problem statement from the README.")

question = st.text_input("Ask a question", placeholder="Which query language does Neo4j use?")
if question:
    result = get_pipeline().ask(question)
    st.markdown(result.answer)
    st.caption(f"Sources: {', '.join(result.sources) or 'none'} | {result.latency_ms} ms")
    with st.expander("Retrieved passages"):
        st.json(result.retrieved)
