import os

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Astrologer", page_icon="🔮")
st.title("🔮 AI Astrologer")
st.caption("Ask our astrologer anything about astrology - zodiac signs, horoscopes, birth charts, compatibility, and more.")

query = st.text_area("Your question", placeholder="e.g. What does it mean if I'm a Scorpio rising?")
ask_clicked = st.button("Ask", type="primary")

if ask_clicked:
    if not query.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Consulting the stars..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"query": query},
                    timeout=40,
                )
            except requests.exceptions.RequestException:
                st.error("Could not reach the backend service. Is it running?")
            else:
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("in_scope", True):
                        st.info(data["answer"])
                    else:
                        st.success(data["answer"])
                else:
                    try:
                        detail = response.json().get("detail", "Something went wrong.")
                    except ValueError:
                        detail = "Something went wrong."
                    st.error(detail)
