import os
from dotenv import load_dotenv
import streamlit as st
from typing import List, Dict
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Constants ---
LEGAL_DOMAINS = [
    "All Laws",
    "IPC (Indian Penal Code)",
    "CrPC (Criminal Procedure Code)",
    "Civil Law",
    "Family Law",
    "Cyber Law",
    "Constitutional Law",
    "Consumer Law",
    "Property Law",
    "Labour Law",
]
DISCLAIMER = """
:warning: **Disclaimer:** This chatbot provides information based on Indian law for educational purposes only. It is not official legal advice. For specific cases, please consult a certified lawyer.
"""

# --- Utility Functions ---
def get_gemini_response(messages: List[Dict], legal_domain: str) -> str:
    """
    Integrates with Gemini 2.0 Flash API to fetch responses.
    """
    system_prompt = (
        "You are a knowledgeable and precise Indian legal assistant. "
        "Provide concise answers based on Indian law (IPC, CrPC, Civil Law, etc.). "
        "If the law is unclear, say 'Please consult a certified lawyer for this specific case.' "
        "Do not fabricate any legal rules."
    )
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat(history=[
        {"role": "user", "parts": [system_prompt]},
        *[{"role": m["role"], "parts": [m["content"]]} for m in messages]
    ])
    response = chat.send_message(messages[-1]["content"])
    return response.text

# --- Streamlit UI ---
st.set_page_config(page_title="Indian Legal Law Chatbot", page_icon="⚖️", layout="centered")
st.title("⚖️ Indian Legal Law Chatbot")

# Sidebar: Legal Domain Selection
st.sidebar.header("Select Legal Domain")
selected_domain = st.sidebar.selectbox("Domain", LEGAL_DOMAINS)

# Sidebar: Keyword Suggestions (Optional)
st.sidebar.markdown("**Keyword Suggestions:**")
st.sidebar.write(
    "Fundamental Rights, IPC Section 420, Cybercrime laws, Divorce procedure, Bail, FIR, Consumer rights, Property dispute, Labour rights"
)

# Disclaimer
st.markdown(DISCLAIMER)

# --- Session State for Chat History and Input Key ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# --- Chat History Panel ---
st.subheader("Chat History")
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Legal Assistant:** {msg['content']}")

# --- User Input (auto-response on Enter, no button) ---
def handle_input():
    user_input = st.session_state.user_input
    if user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Fetching response from legal assistant..."):
            response = get_gemini_response(st.session_state.chat_history, selected_domain)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.user_input = ""  # Clear input after response

st.text_input(
    "Ask your legal question:",
    key="user_input",
    on_change=handle_input,
)

# --- Mobile Friendly Note ---
st.caption("Powered by Gemini 2.0 Flash API (Google AI).")
