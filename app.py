import base64
import os
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components

API_BASE_URL = os.getenv("AGRI_API_URL", "http://127.0.0.1:8000").rstrip("/")
PAGE_ICON = Path(__file__).resolve().parent / \
    "assets" / "agri_mithran_icon.svg"
BACKGROUND_IMAGE = (
    Path(__file__).resolve().parent / "assets" / "farmland_background.svg"
)
BACKGROUND_IMAGE_DATA = base64.b64encode(
    BACKGROUND_IMAGE.read_bytes()
).decode("ascii")


def clear_search_query():
    st.session_state.search_query = ""


# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AgriMithran - TN Agriculture Schemes RAG",
    page_icon=str(PAGE_ICON),
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- 3. SIDEBAR: CONTROLS, THEME & REFRESH ---
with st.sidebar:
    st.image(
        str(PAGE_ICON), width=80
    )  # Agri icon
    st.title("AgriMithran Controls")
    st.write(
        "AI-Powered Assistant for Tamil Nadu Agriculture Schemes (2026-2027)."
    )

    st.divider()

    theme = st.selectbox("🎨 Theme", ("Light", "Dark"), key="app_theme")

    st.button(
        "🔄 Refresh Application",
        use_container_width=True,
        on_click=clear_search_query,
        key="refresh_application",
    )

    st.divider()
    with st.container(key="about_panel"):
        st.markdown("#### 🌱 Your scheme guide")
        st.caption(
            "Explore Tamil Nadu farm schemes, subsidies, eligibility, and "
            "application steps in Tamil or English."
        )

# --- 4. APPLY SELECTED THEME ---
if theme == "Dark":
    page_background = "#0e1117"
    surface_background = "#1b1f27"
    raised_surface = "#252b36"
    text_color = "#fafafa"
    muted_text = "#c5ccd6"
    border_color = "#3b414d"
    about_panel_background = "#222a35"
    about_panel_heading = "#e8f5e9"
    about_panel_caption = "#d5dee8"
    about_panel_accent = "#81c784"
    background_overlay = "rgba(10, 14, 18, 0.78)"
    refresh_button_background = "#245b32"
    refresh_button_hover = "#2e7d42"
    primary_button_background = "#2e7d32"
    alert_background = "#202733"
else:
    page_background = "#ffffff"
    surface_background = "#f1f8e9"
    raised_surface = "#ffffff"
    text_color = "#263238"
    muted_text = "#52615b"
    border_color = "#d5dfd0"
    about_panel_background = "#edf7ef"
    about_panel_heading = "#1b5e20"
    about_panel_caption = "#455a64"
    about_panel_accent = "#2e7d32"
    background_overlay = "rgba(255, 255, 255, 0.78)"
    refresh_button_background = "#e8f5e9"
    refresh_button_hover = "#dcedc8"
    primary_button_background = "#2e7d32"
    alert_background = "#f1f8e9"

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-color: {page_background};
        background-image:
            linear-gradient(
                {background_overlay},
                {background_overlay}
            ),
            url("data:image/svg+xml;base64,{BACKGROUND_IMAGE_DATA}");
        background-position: center;
        background-size: cover;
        background-attachment: fixed;
        color: {text_color};
    }}
    [data-testid="stHeader"] {{
        background-color: {page_background};
    }}
    [data-testid="stSidebar"] {{
        background-color: {surface_background};
    }}
    [data-testid="stMain"] {{
        color: {text_color};
    }}
    [data-testid="stMarkdownContainer"] :is(p, h1, h2, h3, h4, h5, h6, li),
    label {{
        color: {text_color};
    }}
    .stTextInput input,
    [data-testid="stSelectbox"] [role="group"] {{
        background-color: {surface_background};
        color: {text_color};
        border-color: {border_color};
    }}
    [data-testid="stSelectbox"] [role="group"] input,
    [data-testid="stSelectbox"] [role="group"] button {{
        color: {text_color};
    }}
    [role="listbox"],
    [role="option"] {{
        background-color: {raised_surface};
        color: {text_color};
    }}
    .stTextInput input::placeholder {{
        color: {muted_text};
        opacity: 0.65;
    }}
    [data-testid="stStatusWidget"],
    [data-testid="stExpander"] {{
        background-color: {surface_background};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 0.75rem;
    }}
    [data-testid="stAlert"] {{
        background-color: {alert_background};
        color: {text_color};
        border: 1px solid {border_color};
    }}
    [data-testid="stAlert"] :is(p, span) {{
        color: {text_color};
    }}
    [data-testid="stButton"] button[kind="primary"] {{
        background-color: {primary_button_background};
        color: #ffffff;
        border: 1px solid {primary_button_background};
    }}
    [data-testid="stButton"] button[kind="primary"]:hover {{
        background-color: {refresh_button_hover};
        border-color: {refresh_button_hover};
        color: #ffffff;
    }}
    .st-key-refresh_application button {{
        background-color: {refresh_button_background};
        color: {text_color};
        border: 1px solid {border_color};
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }}
    .st-key-refresh_application button:hover {{
        background-color: {refresh_button_hover};
        border-color: {refresh_button_hover};
        color: {text_color};
    }}
    .st-key-about_panel {{
        background-color: {about_panel_background};
        border: 1px solid {border_color};
        border-left: 4px solid {about_panel_accent};
        border-radius: 0.85rem;
        padding: 0.85rem 1rem 0.7rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
    }}
    .st-key-about_panel h4 {{
        margin: 0 0 0.35rem;
        color: {about_panel_heading};
        font-size: 1rem;
    }}
    .st-key-about_panel [data-testid="stCaptionContainer"],
    .st-key-about_panel [data-testid="stCaptionContainer"] p {{
        color: {about_panel_caption};
        line-height: 1.5;
    }}
    .main {{
        padding: 2rem;
    }}
    .scheme-card {{
        padding: 20px;
        border-radius: 12px;
        border: 1px solid {border_color};
        background-color: {surface_background};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }}
    .scheme-card:hover {{
        transform: translateY(-2px);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --- 5. MAIN APP HEADER WITH ANIMATED BADGE ---
title_icon, title_text = st.columns([0.1, 0.9], vertical_alignment="center")
with title_icon:
    st.image(str(PAGE_ICON), width=48)
with title_text:
    st.title("Tamil Nadu Agriculture Schemes Assistant")
st.markdown(
    "Explore verified subsidies, grants, and agricultural engineering schemes"
    " instantly using secure **Self-RAG** technology."
)
st.markdown("---")

# --- 6. USER INPUT SEARCH SECTION ---
query = st.text_input(
    "🔍 Ask your question about any scheme:",
    placeholder=(
        "e.g., What is the subsidy for certified seeds or replacement of"
        " pumpsets?"
    ),
    key="search_query",
)
if not st.session_state.get("_initial_search_focus_done", False):
    components.html(
        """
        <script>
        const parentDocument = window.parent.document;
        let attempts = 0;
        const focusSearchInput = window.setInterval(() => {
            const searchInput = parentDocument.querySelector(
                '[data-testid="stTextInput"] input'
            );
            attempts += 1;
            if (searchInput) {
                window.clearInterval(focusSearchInput);
                if (parentDocument.activeElement === parentDocument.body) {
                    searchInput.focus();
                }
            } else if (attempts >= 20) {
                window.clearInterval(focusSearchInput);
            }
        }, 50);
        </script>
        """,
        height=0,
    )
    st.session_state["_initial_search_focus_done"] = True

response_language = st.selectbox(
    "🌐 Response language",
    ("Tamil", "English"),
    key="response_language",
)

search_clicked = st.button("🚀 Search Schemes", type="primary")

# --- 7. SEARCH & GENERATION LOGIC ---
if search_clicked:
    if not query.strip():
        st.warning("⚠️ Please enter a valid question before searching.")
    else:
        with st.status(
            "🤖 Processing query with the local FAISS index...", expanded=True
        ) as status:
            st.write("🔍 Searching the local agriculture scheme database...")
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/search",
                    json={"query": query, "language": response_language},
                    timeout=120,
                )
                response.raise_for_status()
            except requests.exceptions.HTTPError as error:
                status.update(label="❌ Search failed.", state="error")
                try:
                    detail = error.response.json().get("detail", str(error))
                except (AttributeError, ValueError):
                    detail = str(error)
                st.error(f"Search request rejected: {detail}")
            except requests.exceptions.RequestException as error:
                status.update(label="❌ API unavailable.", state="error")
                st.error(
                    "Could not connect to the AgriMithran API. Start it with "
                    "`uvicorn backend.api:app --reload` and verify AGRI_API_URL. "
                    f"Details: {error}"
                )
            else:
                result = response.json()
                status.update(
                    label="✅ Scheme details retrieved successfully!",
                    state="complete",
                    expanded=True,
                )

                st.success("🎉 Scheme Details Found!")
                answer = result["answer"]
                st.markdown(
                    f"### 🌾 {answer['scheme_name']}"
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 💰 Funding & Subsidy")
                    st.info(answer["funding_pattern"])

                with col2:
                    st.markdown("#### 👥 Eligibility")
                    st.success(answer["eligibility"])

                st.markdown("#### 📝 How to Apply")
                st.write(answer["how_to_apply"])

                with st.expander("🔍 Evaluation & retrieved source documents"):
                    evaluation = result["evaluation"]
                    metric_columns = st.columns(4)
                    metrics = (
                        ("Overall", "overall_score"),
                        ("Faithfulness", "faithfulness_score"),
                        ("Answer relevance", "answer_relevance_score"),
                        ("Retrieval relevance", "retrieval_relevance_score"),
                    )
                    for column, (label, metric_key) in zip(
                        metric_columns,
                        metrics,
                    ):
                        score = evaluation[metric_key]
                        column.metric(label, f"{score:.1f}/100")
                        column.progress(score / 100)

                    verdict = evaluation["verdict"]
                    st.write(
                        f"**Evaluation:** {verdict} — {evaluation['reason']}"
                    )
                    st.caption(
                        "Retrieval relevance is the percentage of retrieved "
                        "documents judged relevant "
                        f"({evaluation['relevant_document_count']} of "
                        f"{evaluation['retrieved_document_count']}). Overall "
                        "score is the mean of the three scores above. "
                        "Faithfulness and answer relevance are AI-estimated; "
                        "PASS requires every score to be at least 70."
                    )
                    for index, source in enumerate(result["sources"], start=1):
                        st.markdown(f"**Source {index}:** {source['source']}")
                        st.write(source["content"])
