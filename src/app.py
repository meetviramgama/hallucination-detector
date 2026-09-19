"""
Hallucination Detector — Streamlit Dashboard (Clean Light Theme)
Run:  streamlit run src/app.py
"""

import os
import sys
import html
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = Path(__file__).parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from pipeline.pipeline import run

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hallucination Detector · AI Fact Checker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ─────────────────────────────────────────────────────────────
for key, val in {
    "history": [],
    "total_verified": 0,
    "total_false": 0,
    "total_unver": 0,
    "total_queries": 0,
    "last_result": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Styling: Clean White & Modern Light Theme ─────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* Global Font & White Background */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1360px !important;
}

/* Sidebar Light Theme */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #0f172a !important;
    font-weight: 700 !important;
}

/* Hero Section */
.hero-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 12px;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.8px;
    line-height: 1.2;
    margin-bottom: 8px;
}

.hero-desc {
    font-size: 1rem;
    color: #64748b;
    line-height: 1.6;
    max-width: 760px;
    margin: 0;
}

/* Input & Button Styling */
.stTextInput input {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    color: #0f172a !important;
    font-size: 1rem !important;
    padding: 12px 16px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}

.stTextInput input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}

.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.2s ease !important;
}

.stButton button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
}

.stButton button:not([kind="primary"]) {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}

.stButton button:not([kind="primary"]):hover {
    border-color: #2563eb !important;
    color: #2563eb !important;
    background-color: #f8fafc !important;
}

/* Verdict Banner */
.verdict-banner {
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.verdict-icon {
    font-size: 3rem;
    line-height: 1;
}

.verdict-info {
    flex: 1;
}

.verdict-title {
    font-size: 1.5rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 4px;
}

.verdict-sub {
    font-size: 0.95rem;
    opacity: 0.9;
    line-height: 1.4;
}

.verdict-score-box {
    text-align: center;
    padding: 8px 20px;
    border-radius: 12px;
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.verdict-score-num {
    font-size: 2.8rem;
    font-weight: 900;
    line-height: 1;
}

.verdict-score-lbl {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    color: #64748b;
    margin-top: 4px;
}

/* Stat Cards */
.stat-card-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}

.stat-card-white {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.stat-card-num {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
}

.stat-card-lbl {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    margin-top: 4px;
}

/* Stacked Accuracy Bar */
.progress-bar-wrap {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.progress-track {
    height: 14px;
    border-radius: 7px;
    background: #f1f5f9;
    overflow: hidden;
    display: flex;
    margin-bottom: 10px;
}

.progress-seg {
    height: 100%;
    transition: width 0.3s ease;
}

.progress-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    font-size: 0.82rem;
    color: #475569;
    font-weight: 500;
}

/* Container & Column Overflow Protections */
[data-testid="column"] {
    min-width: 0 !important;
    overflow-wrap: break-word !important;
}

[data-testid="stHorizontalBlock"] {
    overflow: hidden !important;
}

/* Answer & Claim Cards */
.white-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    line-height: 1.75;
    font-size: 0.98rem;
    color: #1e293b;
    max-width: 100% !important;
    overflow-x: auto !important;
    box-sizing: border-box !important;
    word-break: break-word !important;
}

/* Responsive Tables: NEVER overlap adjacent columns */
.white-box table, [data-testid="column"] table, .stMarkdown table {
    display: block !important;
    max-width: 100% !important;
    width: 100% !important;
    overflow-x: auto !important;
    border-collapse: collapse !important;
    margin: 16px 0 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
}

.white-box th, .white-box td, [data-testid="column"] th, [data-testid="column"] td, .stMarkdown th, .stMarkdown td {
    padding: 10px 14px !important;
    border: 1px solid #e2e8f0 !important;
    font-size: 0.88rem !important;
    text-align: left !important;
    vertical-align: top !important;
    word-break: normal !important;
    white-space: normal !important;
}

.white-box th, [data-testid="column"] th, .stMarkdown th {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    font-weight: 700 !important;
}

.section-heading {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.claim-card-clean {
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    border: 1.5px solid;
    background: #ffffff;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    max-width: 100% !important;
    overflow-x: auto !important;
    box-sizing: border-box !important;
}

.claim-header-clean {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    gap: 12px;
}

.claim-badge-pill {
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.6px;
    padding: 4px 12px;
    border-radius: 9999px;
}

.claim-text-content {
    font-size: 1rem;
    font-weight: 600;
    color: #0f172a;
    line-height: 1.55;
    margin-bottom: 10px;
}

.claim-evidence-clean {
    margin-top: 10px;
    padding: 12px 16px;
    background: #f8fafc;
    border-radius: 10px;
    border-left: 3.5px solid #cbd5e1;
    font-size: 0.86rem;
    color: #475569;
    line-height: 1.55;
}

.claim-reason-clean {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px dashed #e2e8f0;
    font-size: 0.86rem;
    font-weight: 500;
}

/* Pipeline Timing Flow */
.pipeline-clean-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 20px;
    margin-bottom: 24px;
    font-size: 0.82rem;
    color: #64748b;
}

.pipeline-step-item {
    text-align: center;
}

.pipeline-step-title {
    font-weight: 700;
    color: #0f172a;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.pipeline-step-time {
    color: #2563eb;
    font-weight: 600;
    margin-top: 2px;
}

/* History Card */
.hist-card-clean {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 14px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def safe(v):
    return html.escape(str(v)) if v is not None else ""


def get_verdict_style(score: int):
    if score >= 80:
        return {
            "icon": "✅",
            "title": "High Trust — Verified",
            "sub": "Most factual claims have been corroborated by external Wikipedia sources.",
            "color": "#15803d",  # Green-700
            "bg": "#f0fdf4",  # Green-50
            "border": "#bbf7d0",  # Green-200
            "badge": "TRUSTWORTHY",
        }
    if score >= 55:
        return {
            "icon": "⚠️",
            "title": "Mixed Reliability — Review Carefully",
            "sub": "Some claims are verified, but others couldn't be confirmed or are contradictory.",
            "color": "#b45309",  # Amber-700
            "bg": "#fffbeb",  # Amber-50
            "border": "#fde68a",  # Amber-200
            "badge": "MIXED",
        }
    return {
        "icon": "🚨",
        "title": "Hallucinations Detected",
        "sub": "This answer contains false or unverified claims. Do not rely on it without independent verification.",
        "color": "#b91c1c",  # Red-700
        "bg": "#fef2f2",  # Red-50
        "border": "#fecaca",  # Red-200
        "badge": "UNRELIABLE",
    }


def render_claim_card(r, index: int):
    verdict = str(getattr(r, "verdict", "UNVERIFIED")).upper()
    confidence = float(getattr(r, "confidence", 0) or 0)
    claim = safe(getattr(r, "claim", ""))
    reasoning = safe(getattr(r, "reasoning", ""))
    evidence_list = getattr(r, "evidence", []) or []

    if verdict == "VERIFIED":
        color = "#15803d"
        bg = "#f0fdf4"
        border = "#86efac"
        label = "✓ VERIFIED TRUE"
    elif verdict == "FALSE":
        color = "#b91c1c"
        bg = "#fef2f2"
        border = "#fca5a5"
        label = "✗ FALSE — HALLUCINATED"
    else:
        color = "#b45309"
        bg = "#fffbeb"
        border = "#fde68a"
        label = "? UNVERIFIED"

    # Evidence snippets with clickable Wikipedia links
    ev_html = ""
    if evidence_list:
        for ev in evidence_list[:2]:
            raw_title = getattr(ev, "title", "Wikipedia") or "Wikipedia"
            title = safe(raw_title)
            snippet = safe(getattr(ev, "snippet", ""))
            wiki_slug = raw_title.replace(" ", "_")
            wiki_url = f"https://en.wikipedia.org/wiki/{wiki_slug}"
            if snippet:
                ev_html += (
                    f'<div class="claim-evidence-clean">'
                    f'<div style="margin-bottom:4px;">'
                    f'<a href="{wiki_url}" target="_blank" style="font-weight:700;color:#2563eb;text-decoration:none;">'
                    f'📖 {title} ↗</a>'
                    f'</div>'
                    f'<div>{snippet}</div>'
                    f'</div>'
                )
    else:
        ev_html = (
            '<div class="claim-evidence-clean" style="color:#94a3b8;font-style:italic;">'
            'No direct Wikipedia evidence snippet retrieved.'
            '</div>'
        )

    reason_html = (
        f'<div class="claim-reason-clean" style="color:{color};"><b>Verification Analysis:</b> {reasoning}</div>'
        if reasoning
        else ""
    )

    card_html = (
        f'<div class="claim-card-clean" style="background:{bg};border-color:{border};">'
        f'<div class="claim-header-clean">'
        f'<div>'
        f'<span style="font-size:0.8rem;font-weight:700;color:#64748b;margin-right:8px;">Claim #{index}</span>'
        f'<span class="claim-badge-pill" style="background:#ffffff;color:{color};border:1.5px solid {border};">'
        f'{label}</span>'
        f'</div>'
        f'<span style="font-size:0.82rem;color:#64748b;font-weight:600;">'
        f'{confidence:.0%} confidence</span>'
        f'</div>'
        f'<div class="claim-text-content">{claim}</div>'
        f'{ev_html}'
        f'{reason_html}'
        f'</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Hallucination Detector")
    st.caption("Factual Claim Verification via Wikipedia")
    st.divider()

    n = st.session_state.total_queries
    v = st.session_state.total_verified
    f = st.session_state.total_false
    u = st.session_state.total_unver
    total_claims_all = v + f + u

    st.markdown(
        f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px;">
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;padding:12px;text-align:center;">
            <div style="font-size:1.5rem;font-weight:800;color:#0f172a;">{n}</div>
            <div style="font-size:0.7rem;color:#64748b;font-weight:700;">QUERIES</div>
        </div>
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;padding:12px;text-align:center;">
            <div style="font-size:1.5rem;font-weight:800;color:#15803d;">{v}</div>
            <div style="font-size:0.7rem;color:#15803d;font-weight:700;">VERIFIED</div>
        </div>
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;padding:12px;text-align:center;">
            <div style="font-size:1.5rem;font-weight:800;color:#b91c1c;">{f}</div>
            <div style="font-size:0.7rem;color:#b91c1c;font-weight:700;">FLAGGED</div>
        </div>
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;padding:12px;text-align:center;">
            <div style="font-size:1.5rem;font-weight:800;color:#b45309;">{u}</div>
            <div style="font-size:0.7rem;color:#b45309;font-weight:700;">UNVERIFIED</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if total_claims_all > 0:
        vp = v / total_claims_all * 100
        up = u / total_claims_all * 100
        fp = f / total_claims_all * 100
        st.markdown(
            f"""
        <div style="margin-bottom:16px;">
            <div style="font-size:0.75rem;font-weight:700;color:#64748b;margin-bottom:6px;">LIFETIME ACCURACY</div>
            <div style="height:10px;border-radius:5px;background:#e2e8f0;overflow:hidden;display:flex;">
                <div style="width:{vp}%;background:#16a34a;"></div>
                <div style="width:{up}%;background:#f59e0b;"></div>
                <div style="width:{fp}%;background:#ef4444;"></div>
            </div>
            <div style="font-size:0.75rem;color:#64748b;margin-top:6px;display:flex;justify-content:space-between;">
                <span>🟢 {vp:.0f}%</span>
                <span>🟡 {up:.0f}%</span>
                <span>🔴 {fp:.0f}%</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("**How Verification Works:**")
    st.markdown(
        """
    1. **Generate** — LLM produces comprehensive answer  
    2. **Extract** — Isolates atomic factual claims  
    3. **Retrieve** — Fetches Wikipedia search snippets  
    4. **Verify** — Validates each claim against evidence
    """
    )

    st.divider()
    st.markdown("**API Settings**")
    existing_key = os.environ.get("GROQ_API_KEY", "")
    if hasattr(st, "secrets") and not existing_key and "GROQ_API_KEY" in st.secrets:
        existing_key = st.secrets["GROQ_API_KEY"]

    has_env_key = bool(existing_key)
    api_key_val = st.text_input(
        "Groq API Key",
        value=st.session_state.get("user_groq_key", ""),
        type="password",
        placeholder="Configured via environment" if has_env_key else "gsk_...",
        help="Provide your Groq API key here if not preset in your deployment environment.",
    )
    if api_key_val.strip():
        os.environ["GROQ_API_KEY"] = api_key_val.strip()
        st.session_state["user_groq_key"] = api_key_val.strip()
    elif has_env_key:
        os.environ["GROQ_API_KEY"] = existing_key

    st.divider()
    if st.button("🗑 Clear Session History", use_container_width=True):
        st.session_state.history = []
        st.session_state.total_verified = 0
        st.session_state.total_false = 0
        st.session_state.total_unver = 0
        st.session_state.total_queries = 0
        st.session_state.last_result = None
        st.rerun()


# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-card">
    <div class="hero-badge">⚡ Automated AI Fact-Checking Engine</div>
    <div class="hero-title">LLM Hallucination Detector</div>
    <p class="hero-desc">
        Evaluate AI generated responses claim-by-claim against trusted real-world knowledge sources.
        Instantly identify accurate statements, hallucinated errors, and unverified information.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Query Input ───────────────────────────────────────────────────────────────
c_in, c_btn = st.columns([5, 1.2])
with c_in:
    query = st.text_input(
        "Query",
        placeholder="e.g. When was the Eiffel Tower constructed and who designed it?",
        label_visibility="collapsed",
        key="query_input",
    )
with c_btn:
    submit = st.button("🔍  Analyse", use_container_width=True, type="primary")

st.markdown(
    '<div style="font-size:0.8rem;color:#64748b;margin: 4px 0 10px 2px;font-weight:600;">Sample questions:</div>',
    unsafe_allow_html=True,
)

ex_cols = st.columns(4)
sample_queries = [
    "Tell me about the Eiffel Tower",
    "Who invented the telephone and when?",
    "Tell me about Marie Curie's Nobel Prizes",
    "What is the population of France?",
]

for col, sample in zip(ex_cols, sample_queries):
    with col:
        lbl = sample[:32] + ("…" if len(sample) > 32 else "")
        if st.button(lbl, use_container_width=True, key=f"ex_{sample}"):
            query = sample
            submit = True

st.markdown("<br>", unsafe_allow_html=True)

# ── API Key Availability Banner ───────────────────────────────────────────────
active_api_key = os.environ.get("GROQ_API_KEY", "")
if not active_api_key:
    st.warning(
        "🔑 **Groq API Key Required**: Please enter your Groq API key in the left sidebar "
        "or configure `GROQ_API_KEY` in environment / Streamlit Secrets to run analysis. "
        "[Get a free API key at Groq Console](https://console.groq.com/keys)."
    )

# ── Processing & Pipeline Execution ───────────────────────────────────────────
if submit and query.strip():
    if not os.environ.get("GROQ_API_KEY"):
        st.error("⚠️ Groq API key is missing. Please enter your API key in the sidebar to proceed.")
    else:
        try:
            with st.spinner(
                "Running pipeline: Generating → Extracting → Retrieving → Verifying…"
            ):
                result = run(query.strip())

            st.session_state.last_result = result
            st.session_state.total_verified += result.trust_score.verified_count
            st.session_state.total_false += result.trust_score.false_count
            st.session_state.total_unver += result.trust_score.unverified_count
            st.session_state.total_queries += 1
            st.session_state.history.append(
                {
                    "query": query.strip(),
                    "score": result.trust_score.score,
                    "label": result.trust_score.label,
                    "verified": result.trust_score.verified_count,
                    "false": result.trust_score.false_count,
                    "unverified": result.trust_score.unverified_count,
                    "total_s": result.total_s,
                }
            )
            # Rerun so sidebar lifetime metrics and claims section refresh in perfect sync
            st.rerun()
        except Exception as exc:
            st.error(f"❌ **Analysis Error**: {exc}")
            st.info(
                "💡 If you encountered an authentication or quota error, "
                "please double-check your Groq API key in the sidebar."
            )

# ── Results Rendering ─────────────────────────────────────────────────────────
if st.session_state.last_result:
    res = st.session_state.last_result

    total_c = res.trust_score.total_claims
    vc = res.trust_score.verified_count
    fc = res.trust_score.false_count
    uc = res.trust_score.unverified_count

    # 1. Metric Stat Cards
    st.markdown(
        f"""
    <div class="stat-card-grid">
        <div class="stat-card-white" style="border-top:3px solid #ef4444;">
            <div class="stat-card-num" style="color:#dc2626;">{fc}</div>
            <div class="stat-card-lbl" style="color:#dc2626;">🚨 FALSE (HALLUCINATED)</div>
        </div>
        <div class="stat-card-white" style="border-top:3px solid #f59e0b;">
            <div class="stat-card-num" style="color:#d97706;">{uc}</div>
            <div class="stat-card-lbl" style="color:#d97706;">⚠️ UNVERIFIED</div>
        </div>
        <div class="stat-card-white" style="border-top:3px solid #10b981;">
            <div class="stat-card-num" style="color:#16a34a;">{vc}</div>
            <div class="stat-card-lbl" style="color:#16a34a;">✅ VERIFIED TRUE</div>
        </div>
        <div class="stat-card-white" style="border-top:3px solid #6366f1;">
            <div class="stat-card-num" style="color:#4f46e5;">{total_c}</div>
            <div class="stat-card-lbl" style="color:#4f46e5;">📊 TOTAL CLAIMS</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 3. Accuracy Progress Bar
    if total_c > 0:
        vp = vc / total_c * 100
        up = uc / total_c * 100
        fp = fc / total_c * 100
        st.markdown(
            f"""
        <div class="progress-bar-wrap">
            <div style="font-size:0.8rem;font-weight:700;color:#0f172a;margin-bottom:8px;">
                CLAIM BREAKDOWN ({total_c} claims analysed)
            </div>
            <div class="progress-track">
                <div class="progress-seg" style="width:{fp}%;background:#ef4444;" title="False"></div>
                <div class="progress-seg" style="width:{up}%;background:#f59e0b;" title="Unverified"></div>
                <div class="progress-seg" style="width:{vp}%;background:#10b981;" title="Verified"></div>
            </div>
            <div class="progress-legend">
                <span style="color:#dc2626;font-weight:600;">🔴 {fc} False ({fp:.0f}%)</span>
                <span style="color:#d97706;font-weight:600;">🟡 {uc} Unverified ({up:.0f}%)</span>
                <span style="color:#16a34a;font-weight:600;">🟢 {vc} Verified ({vp:.0f}%)</span>
                <span style="margin-left:auto;color:#64748b;">Pipeline Total Latency: {res.total_s:.2f}s</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # 3. Latency Timing Flow
    st.markdown(
        f"""
    <div class="pipeline-clean-bar">
        <div class="pipeline-step-item">
            <div class="pipeline-step-title">🧠 1. Generate</div>
            <div class="pipeline-step-time">{res.generator_s:.2f}s</div>
        </div>
        <div>→</div>
        <div class="pipeline-step-item">
            <div class="pipeline-step-title">📝 2. Extract</div>
            <div class="pipeline-step-time">{res.extractor_s:.2f}s</div>
        </div>
        <div>→</div>
        <div class="pipeline-step-item">
            <div class="pipeline-step-title">📚 3. Retrieve</div>
            <div class="pipeline-step-time">{res.retriever_s:.2f}s</div>
        </div>
        <div>→</div>
        <div class="pipeline-step-item">
            <div class="pipeline-step-title">⚖️ 4. Verify</div>
            <div class="pipeline-step-time">{res.verifier_s:.2f}s</div>
        </div>
        <div>→</div>
        <div class="pipeline-step-item">
            <div class="pipeline-step-title">📊 Claims Evaluated</div>
            <div class="pipeline-step-time">{total_c} claims</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 5. Dedicated Sections with View Switcher (No Overlap)
    claims = res.claims or []
    false_claims = [r for r in claims if getattr(r, "verdict", "") == "FALSE"]
    unver_claims = [r for r in claims if getattr(r, "verdict", "") == "UNVERIFIED"]
    ver_claims = [r for r in claims if getattr(r, "verdict", "") == "VERIFIED"]

    c_head, c_mode = st.columns([3, 1.6])
    with c_head:
        st.markdown(
            '<div class="section-heading">Detailed Analysis & Fact-Check</div>',
            unsafe_allow_html=True,
        )
    with c_mode:
        view_mode = st.radio(
            "Layout",
            ["📑 Dedicated Sections", "◫ Side-by-Side Split"],
            horizontal=True,
            label_visibility="collapsed",
            key="analysis_view_mode",
        )

    def render_claims_content():
        if not claims:
            st.info("No extractable factual claims detected.")
            return

        claim_tab_all, claim_tab_false, claim_tab_unver, claim_tab_ver = st.tabs(
            [
                f"📋 All Claims ({len(claims)})",
                f"🚨 Hallucinated ({len(false_claims)})",
                f"⚠️ Unverified ({len(unver_claims)})",
                f"✅ Verified ({len(ver_claims)})",
            ]
        )

        with claim_tab_all:
            if false_claims:
                st.markdown(
                    f'<div style="font-size:0.88rem;font-weight:800;color:#dc2626;margin:8px 0 10px 0;">🚨 HALLUCINATED CLAIMS ({len(false_claims)})</div>',
                    unsafe_allow_html=True,
                )
                for i, r in enumerate(false_claims, 1):
                    render_claim_card(r, i)

            if unver_claims:
                st.markdown(
                    f'<div style="font-size:0.88rem;font-weight:800;color:#d97706;margin:12px 0 10px 0;">⚠️ COULD NOT VERIFY ({len(unver_claims)})</div>',
                    unsafe_allow_html=True,
                )
                for i, r in enumerate(unver_claims, len(false_claims) + 1):
                    render_claim_card(r, i)

            if ver_claims:
                st.markdown(
                    f'<div style="font-size:0.88rem;font-weight:800;color:#15803d;margin:12px 0 10px 0;">✅ VERIFIED CLAIMS ({len(ver_claims)})</div>',
                    unsafe_allow_html=True,
                )
                for i, r in enumerate(ver_claims, len(false_claims) + len(unver_claims) + 1):
                    render_claim_card(r, i)

        with claim_tab_false:
            if false_claims:
                for i, r in enumerate(false_claims, 1):
                    render_claim_card(r, i)
            else:
                st.success("🎉 No hallucinated or false claims detected!")

        with claim_tab_unver:
            if unver_claims:
                for i, r in enumerate(unver_claims, 1):
                    render_claim_card(r, i)
            else:
                st.info("No unverified claims.")

        with claim_tab_ver:
            if ver_claims:
                for i, r in enumerate(ver_claims, 1):
                    render_claim_card(r, i)
            else:
                st.warning("No claims could be positively verified by Wikipedia snippets.")

    def render_answer_box():
        st.markdown(
            '<div style="font-size:0.95rem;font-weight:700;color:#475569;margin-bottom:8px;">💬 Generated LLM Answer</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="white-box">\n\n{res.answer}\n\n</div>',
            unsafe_allow_html=True,
        )

    if view_mode == "📑 Dedicated Sections":
        # 1. Full-Width Answer Section
        render_answer_box()

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Full-Width Dedicated Claims Section
        st.markdown(
            f'<div class="section-heading">🔎 Claim-by-Claim Fact Check ({len(claims)} claims evaluated)</div>',
            unsafe_allow_html=True,
        )
        render_claims_content()
    else:
        # Side-by-Side Split View (with complete overflow and bleed protection)
        col_left, col_right = st.columns([1, 1.15], gap="large")
        with col_left:
            render_answer_box()
        with col_right:
            st.markdown(
                f'<div style="font-size:0.95rem;font-weight:700;color:#475569;margin-bottom:8px;">🔎 Claim-by-Claim Fact Check ({len(claims)})</div>',
                unsafe_allow_html=True,
            )
            render_claims_content()

# ── Session History ───────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-heading">📋 Session Query History</div>',
        unsafe_allow_html=True,
    )
    for i, h in enumerate(reversed(st.session_state.history), 1):
        fc = h.get("false", 0)
        uc = h.get("unverified", 0)
        vc = h.get("verified", 0)
        tot = fc + uc + vc
        if fc > 0:
            badge_color, badge_bg, badge_lbl = "#b91c1c", "#fef2f2", f"🚨 {fc} False"
        elif uc > 0:
            badge_color, badge_bg, badge_lbl = "#b45309", "#fffbeb", f"⚠️ {uc} Unverified"
        else:
            badge_color, badge_bg, badge_lbl = "#15803d", "#f0fdf4", "✅ All Verified"

        st.markdown(
            f"""
        <div class="hist-card-clean">
            <span style="background:{badge_bg};color:{badge_color};padding:4px 10px;border-radius:9999px;font-size:0.75rem;font-weight:800;">
                {badge_lbl}
            </span>
            <div style="flex:1;font-size:0.9rem;font-weight:600;color:#1e293b;">
                {safe(h['query'][:75])}{"…" if len(h['query']) > 75 else ""}
            </div>
            <div style="font-size:0.85rem;font-weight:700;color:#64748b;">
                {tot} claims
            </div>
            <div style="font-size:0.75rem;color:#64748b;">
                🔴 {fc} false &nbsp; 🟡 {uc} unverified &nbsp; 🟢 {vc} verified
                &nbsp;·&nbsp; {h.get('total_s', 0):.1f}s
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
