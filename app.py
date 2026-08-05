import os
import tempfile
from pathlib import Path

import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClipQuery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface-2: #1a1a25;
    --border: #2a2a3a;
    --accent: #7c3aed;
    --accent-glow: #9f67ff;
    --accent-2: #06b6d4;
    --text: #e8e8f0;
    --text-muted: #7070a0;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Animated grid background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hero Title ── */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

.hero-panel {
    display: grid;
    grid-template-columns: minmax(280px, 1.4fr) minmax(240px, 1fr);
    gap: 1.5rem;
    align-items: start;
    margin-bottom: 1.5rem;
}

.hero-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 1.5rem;
}

.hero-card h2 {
    margin: 0;
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 4vw, 3.5rem);
    line-height: 1.05;
}

.hero-card p {
    margin: 1rem 0 0;
    color: var(--text-muted);
    line-height: 1.7;
}

.feature-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    margin: 0.3rem 0.4rem 0 0;
    padding: 0.55rem 0.85rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    color: var(--text-muted);
    font-size: 0.8rem;
}

.hero-layout {
    display: grid;
    grid-template-columns: minmax(500px, 2.3fr) minmax(320px, 1fr);
    gap: 1.75rem;
    align-items: start;
    margin-bottom: 2rem;
}

.sidebar-header {
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.sidebar-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem;
    font-weight: 800;
    margin-bottom: 0.15rem;
}

.sidebar-brand-sub {
    font-size: 0.85rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.recent-analyses {
    margin-top: 2rem;
}

.recent-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
}

.recent-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 1rem;
    min-height: 110px;
}

.recent-card.add-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    text-align: center;
}

.hero-top {
    font-size: 0.9rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.85rem;
}

.hero-highlight {
    color: var(--accent);
}

.chat-box {
    padding: 1rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    min-height: 240px;
    color: var(--text-muted);
    line-height: 1.8;
}

.suggested-question {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.95rem 1rem;
    color: var(--text);
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
}

.suggested-question:hover {
    background: rgba(255,255,255,0.06);
    transform: translateY(-1px);
}

.workflow-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.15rem;
    min-height: 110px;
}

.workflow-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
}

.workflow-card .card-title {
    margin-bottom: 0.75rem;
}

.workflow-card .card-content {
    font-size: 0.88rem;
    color: var(--text-muted);
}

.hero-copy {
    padding: 2rem 2rem 2.25rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 28px;
    position: relative;
}

.hero-copy h1 {
    margin: 0 0 0.8rem;
    font-size: clamp(3rem, 4vw, 4.4rem);
    letter-spacing: -0.04em;
    line-height: 1;
}

.hero-copy p {
    max-width: 640px;
    margin: 0 0 1.75rem;
    color: var(--text-muted);
    line-height: 1.9;
    font-size: 1rem;
}

.hero-actions {
    display: grid;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.input-panel {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 1.4rem;
}

.input-row {
    display: flex;
    align-items: stretch;
    gap: 0.85rem;
    flex-wrap: wrap;
}

.input-secondary {
    flex: 1 1 340px;
}

.input-button {
    background: linear-gradient(135deg, var(--accent), #5b21b6);
    color: white;
    border: none;
    padding: 0.9rem 1.4rem;
    border-radius: 14px;
    font-size: 0.95rem;
    font-weight: 700;
    cursor: pointer;
    width: 100%;
}

.input-button:hover {
    opacity: 0.95;
}

.button-row {
    display: flex;
    gap: 0.85rem;
    flex-wrap: wrap;
    margin-top: 0.7rem;
}

.small-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 1rem;
}

.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    padding: 1rem 0 0;
}

.sidebar-nav a {
    color: var(--text-muted);
    text-decoration: none;
    padding: 0.9rem 1rem;
    border-radius: 12px;
    display: block;
    transition: background 0.2s, color 0.2s;
}

.sidebar-nav a:hover,
.sidebar-nav a.active {
    background: rgba(124,58,237,0.14);
    color: white;
}

.chat-panel {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 1.5rem;
    min-height: 520px;
}

.chat-panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.35rem;
}

.chat-panel-header h3 {
    margin: 0;
    font-size: 1.15rem;
}

.suggested-questions {
    display: grid;
    gap: 0.75rem;
    margin-top: 1.25rem;
}

.suggested-question {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.95rem 1rem;
    color: var(--text-muted);
    cursor: pointer;
}

.workflow-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1.75rem;
}

.workflow-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.15rem;
    min-height: 110px;
}

.workflow-card .card-title {
    margin-bottom: 0.75rem;
}

.workflow-card .card-content {
    font-size: 0.82rem;
    color: var(--text-muted);
}

.input-label {
    font-size: 0.8rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.45rem;
}

.stSidebar {
    color: var(--text) !important;
}

[data-testid="stSidebar"] {
    background: rgba(15, 15, 22, 0.98) !important;
}

[data-testid="stSidebar"] .css-1d391kg {
    border: none !important;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}

.card:hover {
    border-color: var(--accent);
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text);
}

/* ── Extra dashboard classes ── */
.sidebar-header {
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.sidebar-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem;
    font-weight: 800;
    margin-bottom: 0.15rem;
}

.sidebar-brand-sub {
    font-size: 0.85rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.recent-analyses {
    margin-top: 2rem;
}

.recent-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
}

.recent-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 1rem;
    min-height: 110px;
}

.recent-card.add-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    text-align: center;
}

.hero-top {
    font-size: 0.9rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.85rem;
}

.hero-highlight {
    color: var(--accent);
}

.chat-box {
    padding: 1rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    min-height: 240px;
    color: var(--text-muted);
    line-height: 1.8;
}

.suggested-question {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.95rem 1rem;
    color: var(--text);
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
}

.suggested-question:hover {
    background: rgba(255,255,255,0.06);
    transform: translateY(-1px);
}

.workflow-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
}

.workflow-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.15rem;
    min-height: 110px;
}

.workflow-card .card-title {
    margin-bottom: 0.75rem;
}

.workflow-card .card-content {
    font-size: 0.88rem;
    color: var(--text-muted);
}

/* ── Input & Buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.08em !important;
    padding: 0.75rem 1.5rem !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease !important;
    text-transform: uppercase !important;
    box-shadow: 0 12px 28px rgba(124,58,237,0.18) !important;
}

.stButton > button:hover,
.stFileUploader > div > button:hover,
.stFileUploader button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 24px 55px rgba(124,58,237,0.32) !important;
    background: linear-gradient(135deg, #8b5cf6, #22d3ee) !important;
}

.stButton > button:focus,
.stFileUploader > div > button:focus,
.stFileUploader button:focus {
    outline: none !important;
    box-shadow: 0 0 0 4px rgba(124,58,237,0.22) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
}

.panel-compact div {
    color: var(--text-muted);
    line-height: 1.7;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}

.card:hover {
    border-color: var(--accent);
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text);
}

/* ── Accent Badge ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.badge-purple { background: rgba(124,58,237,0.2); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15); color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);    border: 1px solid rgba(16,185,129,0.3); }

/* ── Input & Buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
}

/* ── Progress / Status ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 8px;
    margin: 0.4rem 0;
    border: 1px solid var(--border);
    font-size: 0.8rem;
}

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active   { background: var(--accent-glow); box-shadow: 0 0 8px var(--accent-glow); animation: pulse 1.5s infinite; }
.dot-done     { background: var(--success); }
.dot-pending  { background: var(--border); }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Chat ── */
.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.chat-msg {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.chat-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.chat-bubble {
    display: inline-block;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 90%;
}

.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }

.user-bubble { background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.25); align-self: flex-end; }
.bot-bubble  { background: rgba(6,182,212,0.1);  border: 1px solid rgba(6,182,212,0.2);   align-self: flex-start; }

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Transcript box ── */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Stale Streamlit elements ── */
.stProgress > div > div > div { background: var(--accent) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active"
    if s == "done":    return "dot-done"
    return "dot-pending"

def render_step_bar(label: str, key: str, icon: str):
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-header">'
        '  <div class="sidebar-brand">ClipQuery</div>'
        '  <div class="sidebar-brand-sub">Meeting Intelligence & Video Q&A</div>'
        '</div>'
        '<hr style="border-color:rgba(255,255,255,0.08);margin:1.5rem 0;" />'
        '<div class="input-label">INPUT</div>',
        unsafe_allow_html=True,
    )

    source = st.text_input("", placeholder="Paste YouTube URL here or upload a file", label_visibility="collapsed")
    uploaded_file = st.file_uploader("", type=["mp4", "mov", "mkv", "wav", "mp3", "m4a", "flac"], label_visibility="collapsed")
    st.markdown('<div style="color:var(--text-muted);font-size:0.78rem;margin-top:0.55rem">200MB per file • MP4, MOV, MKV, WAV, MP3, M4A, FLAC</div>', unsafe_allow_html=True)

    language = st.selectbox("", ["English (Auto)", "English", "Hinglish"], index=0, label_visibility="collapsed")

    run_btn = st.button("Analyse Video", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_step_bar(label, step, icon)
        st.markdown('---')
        st.markdown('<div style="font-size:0.85rem;color:var(--text-muted);">Built with ❤️ by <strong>Faizan Raza</strong></div>', unsafe_allow_html=True)

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-panel">'
    '  <div class="hero-card">'
    '    <div class="hero-title">ClipQuery</div>'
    '    <div class="hero-sub">Turn any video into searchable knowledge with fast AI summarization and RAG-powered Q&A.</div>'
    '    <p>Upload a video or paste a YouTube link to run the same analysis pipeline for both. The assistant extracts transcript, summary, action items, decisions, and open questions.</p>'
    '    <div style="margin-top:1.5rem; display:flex; flex-wrap:wrap; gap:0.75rem">'
    '      <span class="feature-pill">🎥 Video upload</span>'
    '      <span class="feature-pill">🧠 RAG Chat</span>'
    '      <span class="feature-pill">📄 Smart Summary</span>'
    '      <span class="feature-pill">🌐 Multi-language</span>'
    '    </div>'
    '  </div>'
    '  <div class="panel-compact">'
    '    <h3>How ClipQuery works</h3>'
    '    <div>Use one unified pipeline for URLs and uploaded videos. Audio extraction, transcript generation, summarization, action item extraction, and intelligent Q&A all run together.</div>'
    '  </div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip() and uploaded_file is None:
        st.error("Please enter a YouTube URL, file path, or upload a file.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        uploaded_path = None
        if uploaded_file is not None:
            tmp_suffix = Path(uploaded_file.name).suffix or ".mp4"
            uploaded_path = tempfile.NamedTemporaryFile(delete=False, suffix=tmp_suffix).name
            with open(uploaded_path, "wb") as f:
                f.write(uploaded_file.read())
            source = uploaded_path

        try:
            with progress_placeholder.container():
                st.info("⚙️ Pipeline running — see sidebar for live status…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error: {e}")

        finally:
            if uploaded_path is not None and os.path.exists(uploaded_path):
                try:
                    os.remove(uploaded_path)
                except OSError:
                    pass

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title banner
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    # Top row: summary + transcript
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    # Second row: action items | decisions | questions
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:700;margin-bottom:1rem">💬 Chat with your Meeting</div>', unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🤖 Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty state
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5rem 2rem;text-align:center">
        <div style="font-size:4rem;margin-bottom:1rem">🎬</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:0.5rem">
            Welcome to ClipQuery
        </div>
        <div style="color:var(--text-muted);font-size:0.85rem;max-width:380px;line-height:1.7">
            Paste a YouTube URL or local file path in the sidebar, choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:2rem;display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)