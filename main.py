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
    Integrates with Gemini 2.0 Flash API to fetch responses, now using the selected legal domain.
    """
    domain_text = f" ({legal_domain})" if legal_domain and legal_domain != "All Laws" else ""
    system_prompt = (
        f"You are a knowledgeable and precise Indian legal assistant. "
        f"Provide concise answers based on Indian law{domain_text}. "
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

# --- Custom Header ---
st.markdown(
    """
    <style>
    .main-header {display: flex; align-items: center; gap: 12px; margin-bottom: 0.5em;}
    .main-title {font-size:2em; font-weight:700; color:#2d3a4a;}
    .disclaimer-box {background-color:#fff3cd; border-left:6px solid #ffecb5; padding:0.8em 1em; margin-bottom:1em; border-radius:6px;}
    .chat-user {background: #e3f2fd; border-radius: 8px; padding: 0.7em 1em; margin-bottom: 0.5em; border: 1px solid #90caf9;}
    .chat-assistant {background: #f1f8e9; border-radius: 8px; padding: 0.7em 1em; margin-bottom: 0.5em; border: 1px solid #aed581;}
    .chat-label {font-weight:600; margin-right:0.5em;}
    .sidebar-title {font-size:1.2em; font-weight:600; color:#2d3a4a; margin-bottom:0.5em;}
    .sidebar-keywords {margin-top:2em; font-weight:600;}
    .sidebar-keywords-list {color:#2d3a4a; font-size:0.98em;}
    .mobile-note {text-align:center; color:#888; margin-top:2em;}
    </style>
    <div class='main-header'>
        <span style='font-size:2.2em;'>⚖️</span>
        <span class='main-title'>Indian Legal Law Chatbot</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar: Legal Domain Selection (with icons)
st.sidebar.markdown(
    "<div class='sidebar-title'>Select Legal Domain</div>", unsafe_allow_html=True)
selected_domain = st.sidebar.selectbox(
    "",
    LEGAL_DOMAINS,
    format_func=lambda d: f"⚖️ {d}" if d != "All Laws" else "📚 All Laws"
)

# Sidebar: Keyword Suggestions (Optional)
st.sidebar.markdown(
    "<div class='sidebar-keywords'>Keyword Suggestions:</div>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<div class='sidebar-keywords-list'>Fundamental Rights, IPC Section 420, Cybercrime laws, Divorce procedure, Bail, FIR, Consumer rights, Property dispute, Labour rights</div>",
    unsafe_allow_html=True
)

# Disclaimer (styled)
st.markdown(
    f"<div class='disclaimer-box'><span style='font-size:1.1em;'>{DISCLAIMER}</span></div>",
    unsafe_allow_html=True
)

# --- Session State for Chat History and Input Key ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# --- Chat History Panel (styled) ---
st.markdown("<div style='margin-bottom:0.5em; font-size:1.2em; font-weight:600;'>Chat History</div>", unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='chat-user'><span class='chat-label'>🧑‍💼 You:</span> {msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='chat-assistant'><span class='chat-label'>🤖 Legal Assistant:</span> {msg['content']}</div>",
            unsafe_allow_html=True
        )

# --- User Input (auto-response on Enter, no button, styled) ---
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
    label_visibility="visible",
    placeholder="Type your legal question and press Enter..."
)

# --- Mobile Friendly Note (styled) ---
st.markdown(
    "<div class='mobile-note'>Powered by <b>Gemini 2.0 Flash API</b> (Google AI).</div>",
    unsafe_allow_html=True
)
