"""
SafeHire AI — Offline Document Verification Assistant
Team Oblivion | Open Innovation Hackathon

Run with:  streamlit run app.py

Full pipeline: OCR -> Forensic (ELA + metadata) -> Semantic match ->
AI-generation detection -> Weighted Semantic Validity Score.
Everything below runs 100% locally — no document data ever leaves this
machine, no network calls are made once dependencies are installed.
"""

import streamlit as st
import plotly.graph_objects as go

from modules.ocr_parser import load_document, run_ocr
from modules.forensics import run_forensics
from modules.semantic_match import semantic_similarity_score, REFERENCE_TEMPLATES
from modules.ai_detector import ai_generation_likelihood
from modules.scorer import compute_validity_score, DEFAULT_WEIGHTS


# ----------------------------- Page setup -----------------------------
st.set_page_config(
    page_title="SafeHire AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


def inject_theme(dark: bool):
    if dark:
        bg, bg2, card, text, sub, accent, accent2, border = (
            "#0E1420", "#141B2A", "#1A2233", "#F2EEFA", "#9AA3B5",
            "#D4AF37", "#FBE695", "#2A3346",
        )
    else:
        bg, bg2, card, text, sub, accent, accent2, border = (
            "#F7F5FB", "#FFFFFF", "#FFFFFF", "#1A1A2E", "#5B5B6B",
            "#B8901F", "#8A6D14", "#E4DEF2",
        )

    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg};
            color: {text};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {bg2};
            border-right: 1px solid {border};
        }}
        h1, h2, h3, h4, p, span, label, .stMarkdown {{
            color: {text} !important;
        }}
        .shai-card {{
            background-color: {card};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 22px 24px;
            margin-bottom: 16px;
        }}
        .shai-hero {{
            background: linear-gradient(135deg, {card} 0%, {bg2} 100%);
            border: 1px solid {accent};
            border-radius: 16px;
            padding: 28px 30px;
            margin-bottom: 22px;
        }}
        .shai-badge {{
            display: inline-block;
            background-color: {accent};
            color: {bg};
            font-weight: 600;
            font-size: 12px;
            padding: 4px 12px;
            border-radius: 20px;
            letter-spacing: 0.5px;
        }}
        .shai-subtle {{ color: {sub} !important; font-size: 14px; }}
        .shai-flag {{
            background-color: {bg2};
            border-left: 3px solid {accent};
            padding: 8px 14px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 6px;
            font-size: 13px;
            color: {text};
        }}
        .stButton>button {{
            background-color: {accent};
            color: {bg};
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px 18px;
        }}
        .stButton>button:hover {{
            background-color: {accent2};
            color: {bg};
        }}
        div[data-testid="stFileUploader"] {{
            background-color: {card};
            border: 1px dashed {accent};
            border-radius: 12px;
            padding: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{ color: {sub}; }}
        .stTabs [aria-selected="true"] {{ color: {accent} !important; }}
    </style>
    """, unsafe_allow_html=True)

    return dict(bg=bg, bg2=bg2, card=card, text=text, sub=sub,
                accent=accent, accent2=accent2, border=border)


palette = inject_theme(st.session_state.dark_mode)


# ----------------------------- Sidebar -----------------------------
with st.sidebar:
    st.markdown("### 🛡️ SafeHire AI")
    st.markdown('<span class="shai-badge">TEAM OBLIVION</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    theme_label = "☀️ Switch to light mode" if st.session_state.dark_mode else "🌙 Switch to dark mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")
    st.markdown("**Document type**")
    doc_type = st.selectbox(
        "doc_type", options=list(REFERENCE_TEMPLATES.keys()),
        format_func=lambda x: x.replace("_", " ").title(),
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Scoring weights**")
    st.caption("Adjust how much each signal contributes to the final score")
    w_ocr = st.slider("OCR confidence", 0.0, 1.0, DEFAULT_WEIGHTS["ocr_confidence"], 0.05)
    w_forensics = st.slider("Forensic integrity", 0.0, 1.0, DEFAULT_WEIGHTS["forensics"], 0.05)
    w_semantic = st.slider("Semantic match", 0.0, 1.0, DEFAULT_WEIGHTS["semantic_match"], 0.05)
    w_ai = st.slider("Human-authorship", 0.0, 1.0, DEFAULT_WEIGHTS["ai_detection"], 0.05)
    total_w = w_ocr + w_forensics + w_semantic + w_ai
    weights = {
        "ocr_confidence": w_ocr / total_w, "forensics": w_forensics / total_w,
        "semantic_match": w_semantic / total_w, "ai_detection": w_ai / total_w,
    } if total_w > 0 else DEFAULT_WEIGHTS

    st.markdown("---")
    with st.expander("⚙️ Tech stack in use"):
        st.markdown("""
        **OCR & parsing:** PyMuPDF, pytesseract (Tesseract)
        **Forensics:** Pillow, NumPy, OpenCV (Error Level Analysis)
        **Semantic match:** scikit-learn (TF-IDF + cosine similarity)
        **AI-text detection:** stylometric heuristics (burstiness, TTR)
        **Production upgrade path:** Ollama local LLM (qwen2.5) for
        perplexity-based AI-detection + embedding-based semantic search via FAISS
        **GUI:** Streamlit + Plotly
        **Runs 100% offline** — no data leaves this machine
        """)


# ----------------------------- Hero header -----------------------------
st.markdown(f"""
<div class="shai-hero">
  <h1 style="margin-bottom:4px;">SafeHire AI</h1>
  <p class="shai-subtle" style="margin-top:0;">
  Offline AI document verification for recruitment — catches fake, tampered,
  or AI-generated resumes, certificates, and ID documents without ever
  sending candidate data to the cloud.
  </p>
</div>
""", unsafe_allow_html=True)


# ----------------------------- Upload -----------------------------
uploaded = st.file_uploader(
    "Upload a document to verify (PDF, PNG, or JPG)",
    type=["pdf", "png", "jpg", "jpeg"],
)

run_clicked = st.button("🔍 Run verification", disabled=uploaded is None)

if uploaded and run_clicked:
    file_bytes = uploaded.read()

    with st.spinner("Running offline verification pipeline..."):
        images, metadata = load_document(file_bytes, uploaded.name)
        extracted_text, ocr_confidence = run_ocr(images)
        forensic_result = run_forensics(images, metadata)
        semantic_score, _ = semantic_similarity_score(extracted_text, doc_type)
        ai_human_score, ai_signals = ai_generation_likelihood(extracted_text)

        final_score, breakdown, verdict = compute_validity_score(
            ocr_confidence, forensic_result["combined_score"],
            semantic_score, ai_human_score, weights,
        )

    st.markdown("---")

    # ----------------------------- Results: score + verdict -----------------------------
    col1, col2 = st.columns([1, 1.4])

    with col1:
        gauge_color = (palette["accent"] if final_score >= 75
                        else "#E0A62C" if final_score >= 50 else "#D8544B")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=final_score,
            number={"suffix": "%", "font": {"color": palette["text"], "size": 40}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": palette["sub"]},
                "bar": {"color": gauge_color},
                "bgcolor": palette["card"],
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": palette["bg2"]},
                    {"range": [50, 75], "color": palette["bg2"]},
                    {"range": [75, 100], "color": palette["bg2"]},
                ],
            },
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=280, margin=dict(l=20, r=20, t=30, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"""
        <div class="shai-card" style="text-align:center;">
          <span class="shai-badge" style="background-color:{gauge_color};">{verdict.upper()}</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="shai-card">', unsafe_allow_html=True)
        st.markdown("#### Signal breakdown")
        bar_fig = go.Figure(go.Bar(
            x=list(breakdown.values()), y=list(breakdown.keys()),
            orientation="h", marker_color=palette["accent"],
            text=[f"{v}%" for v in breakdown.values()], textposition="outside",
        ))
        bar_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=220, margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[0, 110], color=palette["sub"], gridcolor=palette["border"]),
            yaxis=dict(color=palette["text"]),
            font=dict(color=palette["text"]),
        )
        st.plotly_chart(bar_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------- Forensics detail -----------------------------
    tab1, tab2, tab3 = st.tabs(["🔬 Forensic analysis", "📄 Extracted text", "🧾 Metadata"])

    with tab1:
        fcol1, fcol2 = st.columns([1, 1])
        with fcol1:
            st.image(forensic_result["heatmap"], caption="Error Level Analysis heatmap "
                      "— bright regions indicate inconsistent compression history",
                      use_container_width=True)
        with fcol2:
            st.metric("ELA integrity score", f"{forensic_result['ela_score']}%")
            st.metric("Metadata integrity score", f"{forensic_result['meta_score']}%")
            if forensic_result["flags"]:
                st.markdown("**Flags raised:**")
                for flag in forensic_result["flags"]:
                    st.markdown(f'<div class="shai-flag">⚠️ {flag}</div>', unsafe_allow_html=True)
            else:
                st.success("No forensic red flags detected")

    with tab2:
        st.text_area("OCR output", extracted_text, height=250)
        st.caption(f"Average OCR confidence: {ocr_confidence}%")
        st.caption(f"Stylometric signals — burstiness: {ai_signals.get('burstiness', 'n/a')}, "
                    f"type-token ratio: {ai_signals.get('type_token_ratio', 'n/a')}")

    with tab3:
        st.json(metadata)

elif uploaded is None:
    st.info("Upload a resume, certificate, ID proof, or offer letter to begin verification.")
