"""
India Consumer Pulse AI — Main Streamlit Application

Entry point: streamlit run app.py

Pipeline flow:
  User input → Apify scrape (or sample) → Clean → AI classify → AI insights → Dashboard
"""

import logging
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from config.settings import settings
from scrapers.apify_scraper import scrape_data
from processing.cleaner import clean_dataframe
from processing.classifier import classify_dataframe
from insights.generator import generate_insights
from dashboard.components import (
    build_brand_context,
    render_brand_filter,
    render_brand_correspondence_map,
    render_overview_metrics,
    render_source_mix_and_sentiment,
    render_brand_sentiment,
    render_themes_and_pain_points,
    render_narratives,
    render_executive_summary,
    render_recommendations,
    render_download_section,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="India Consumer Pulse AI",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='color:#1a1a2e; margin-bottom:0'>🇮🇳 India Consumer<br>Pulse AI</h2>",
        unsafe_allow_html=True,
    )
    st.caption("Consumer Intelligence for the Indian Market")
    st.divider()

    category = st.selectbox(
        "Category",
        options=["Consumer Tech India"],
        help="More categories (EV, FMCG, Wellness) coming in Phase 2.",
    )

    keywords_input = st.text_area(
        "Keywords (comma-separated)",
        value="AI laptops, premium laptops, smartphone upgrade, MacBook, Lenovo ThinkPad",
        height=90,
        help="Topics to search for. Separate with commas.",
    )

    _PRESET_BRANDS = [
        "Apple", "Lenovo", "HP", "Dell", "ASUS", "Acer", "MSI",
        "Samsung", "OnePlus", "Xiaomi", "Realme", "Vivo", "OPPO",
        "boAt", "Noise", "Nothing",
    ]
    brands_selected = st.multiselect(
        "Brands to track",
        options=_PRESET_BRANDS,
        default=["Apple", "Lenovo", "HP", "Dell", "ASUS"],
        help="Select brands from the list below.",
    )
    custom_brands_raw = st.text_input(
        "Add custom brands",
        placeholder="e.g. Acer, realme GT, Nothing Phone",
        help="Comma-separated. Adds brands not in the list above.",
    )
    if custom_brands_raw.strip():
        _extra = [b.strip() for b in custom_brands_raw.split(",") if b.strip()]
        brands_selected = list(dict.fromkeys(brands_selected + _extra))

    _SOURCE_OPTIONS = ["Reddit India", "YouTube", "Google News", "Sample Data"]
    data_sources = st.multiselect(
        "Data Sources",
        options=_SOURCE_OPTIONS,
        default=["Reddit India"],
        help=(
            "Select one or more sources. Requires APIFY_API_TOKEN in .env for live scraping. "
            "Select 'Sample Data' to use the built-in dataset with no API key needed."
        ),
    )
    if not data_sources:
        data_sources = ["Sample Data"]

    st.markdown("**Analysis Period**")
    _col_d1, _col_d2 = st.columns(2)
    with _col_d1:
        date_from = st.date_input("From", value=date.today() - timedelta(days=7),
                                  max_value=date.today())
    with _col_d2:
        date_to = st.date_input("To", value=date.today(), max_value=date.today())

    if date_from > date_to:
        st.warning("'From' date must be before 'To' date.")

    _days = max(1, (date_to - date_from).days + 1)
    if _days > 30:
        st.caption(
            f"⚠️ {_days}-day range selected. Large datasets take longer and use "
            "more API tokens. Consider narrowing the window for testing."
        )
    else:
        st.caption(f"Fetching {_days} day{'s' if _days != 1 else ''} of conversations.")

    st.divider()

    # Status indicators
    apify_ok = settings.apify_configured
    openrouter_ok = settings.openrouter_configured

    st.markdown("**Connection Status**")
    st.markdown(
        f"{'✅' if apify_ok else '⚠️'} Apify — "
        f"{'Connected' if apify_ok else 'Not configured (using sample data)'}"
    )
    st.markdown(
        f"{'✅' if openrouter_ok else '⚠️'} OpenRouter — "
        f"{'Connected' if openrouter_ok else 'Not configured (using keyword fallback)'}"
    )

    if not apify_ok or not openrouter_ok:
        st.caption("Add keys to `.env` file. See `.env.example` for reference.")

    st.divider()
    run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    load_last_button = st.button("📂 Load Last Run", use_container_width=True,
                                  help="Reload the most recent saved analysis instantly.")

# ── Main header ───────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#1a1a2e; margin-bottom:4px'>🇮🇳 India Consumer Pulse AI</h1>",
    unsafe_allow_html=True,
)
st.caption(
    "Strategic consumer intelligence for Indian brands — "
    "built on digital conversations, powered by AI, calibrated for India."
)
st.divider()

# ── Load last saved run ───────────────────────────────────────
if load_last_button:
    import glob as _glob
    _processed_files = sorted(
        _glob.glob(f"{settings.PROCESSED_DATA_DIR}/processed_*.csv"),
        reverse=True,
    )
    _raw_files = sorted(
        _glob.glob(f"{settings.RAW_DATA_DIR}/raw_*.csv"),
        reverse=True,
    )
    if not _processed_files:
        st.warning("No previous runs found. Click Run Analysis to generate your first report.")
        st.stop()

    _load_bar = st.progress(0, text="Loading previous analysis...")
    try:
        _load_bar.progress(20, text="Reading saved data...")
        _df_proc = pd.read_csv(_processed_files[0])
        _df_raw = pd.read_csv(_raw_files[0]) if _raw_files else _df_proc.copy()
        _ts = os.path.basename(_processed_files[0]).replace("processed_", "").replace(".csv", "")
        _ts_fmt = f"{_ts[:4]}-{_ts[4:6]}-{_ts[6:8]} {_ts[9:11]}:{_ts[11:13]}"

        _load_bar.progress(60, text=f"Regenerating insights for {len(_df_proc):,} conversations...")
        _last_brands = list(_df_proc["brand"].unique()) if "brand" in _df_proc.columns else brands_selected
        _last_brands = [b for b in _last_brands if b != "Other"]
        _last_keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        _insights = generate_insights(_df_proc, category, _last_brands, _last_keywords)

        _load_bar.progress(95, text="Finalising...")
        _insights["_df"] = _df_proc
        st.session_state["df_raw"] = _df_raw
        st.session_state["df_processed"] = _df_proc
        st.session_state["insights"] = _insights
        st.session_state["run_config"] = {
            "category": category,
            "keywords": _last_keywords,
            "brands": _last_brands,
            "source": "Previous run",
            "date_from": str(_df_proc["date"].min()) if "date" in _df_proc.columns else "",
            "date_to": str(_df_proc["date"].max()) if "date" in _df_proc.columns else "",
            "timestamp": _ts_fmt,
        }
        _load_bar.progress(100, text="Loaded.")
        st.rerun()
    except Exception as _e:
        logger.exception("Load last run failed")
        st.error(f"Could not load previous run: {_e}")
        st.stop()


# ── Pipeline execution ────────────────────────────────────────
if run_button:
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

    if not keywords:
        st.warning("Please enter at least one keyword before running analysis.")
        st.stop()

    if not brands_selected:
        st.warning("Please select at least one brand to track.")
        st.stop()

    progress_bar = st.progress(0, text="Starting analysis pipeline...")

    _date_from_str = date_from.strftime("%Y-%m-%d")
    _date_to_str = date_to.strftime("%Y-%m-%d")

    # Stage 1: Scrape
    _apify_sources = [s for s in data_sources if s in ("YouTube", "Amazon Reviews", "Google News")]
    _scrape_msg = f"Fetching conversations ({_date_from_str} to {_date_to_str})"
    if _apify_sources:
        _scrape_msg += f" — {', '.join(_apify_sources)} run via Apify in parallel (up to 3 min)"
    try:
        progress_bar.progress(10, text=_scrape_msg + "...")
        df_raw = scrape_data(
            data_sources, keywords, brands_selected,
            _date_from_str, _date_to_str, category,
        )
        if df_raw.empty:
            st.error("No data fetched. Check your Apify token or switch to 'Sample Data'.")
            st.stop()
    except Exception as e:
        logger.exception("Stage 1 (scrape) failed")
        st.error(f"Scraping failed: {e}")
        st.stop()

    # Stage 2: Clean
    try:
        progress_bar.progress(30, text=f"Cleaning {len(df_raw):,} records...")
        df_clean = clean_dataframe(df_raw)
        if df_clean.empty:
            st.warning("No records survived cleaning. Try a wider date range or broader keywords.")
            st.stop()
    except Exception as e:
        logger.exception("Stage 2 (clean) failed")
        st.error(f"Cleaning failed: {e}")
        st.stop()

    # Stage 3: Classify
    try:
        n = len(df_clean)
        ai_n = min(n, 500)
        progress_bar.progress(
            55,
            text=f"Classifying {n:,} records — AI on top {ai_n:,}, keyword on rest...",
        )
        df_processed = classify_dataframe(df_clean, category, brands_selected)
    except Exception as e:
        logger.exception("Stage 3 (classify) failed")
        st.error(f"Classification failed: {e}")
        st.stop()

    # Stage 4: Insights — non-fatal: show dashboard even if insights partially fail
    try:
        progress_bar.progress(80, text="Generating strategic insights (executive summary + narratives)...")
        insights = generate_insights(df_processed, category, brands_selected, keywords)
    except Exception as e:
        logger.exception("Stage 4 (insights) failed — continuing with empty insights")
        st.warning(f"Insight generation encountered an error ({e}). Dashboard will show data without AI narratives.")
        insights = {"executive_summary": "", "dominant_narratives": [], "strategic_recommendations": [], "data_summary": {}}

    # Stage 5: Save — non-fatal
    try:
        progress_bar.progress(95, text="Saving outputs...")
        os.makedirs(settings.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        df_raw.to_csv(f"{settings.RAW_DATA_DIR}/raw_{ts}.csv", index=False)
        df_processed.to_csv(f"{settings.PROCESSED_DATA_DIR}/processed_{ts}.csv", index=False)
    except Exception as e:
        logger.warning(f"Stage 5 (save) failed — dashboard will still render: {e}")

    # Store results and render dashboard
    insights["_df"] = df_processed  # used by render_narratives brand lens
    st.session_state["df_raw"] = df_raw
    st.session_state["df_processed"] = df_processed
    st.session_state["insights"] = insights
    st.session_state["run_config"] = {
        "category": category,
        "keywords": keywords,
        "brands": brands_selected,
        "source": ", ".join(data_sources),
        "date_from": _date_from_str,
        "date_to": _date_to_str,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    progress_bar.progress(100, text="Analysis complete.")
    st.rerun()

# ── Dashboard rendering ───────────────────────────────────────
if "df_processed" in st.session_state:
    df_raw = st.session_state["df_raw"]
    df_processed = st.session_state["df_processed"]
    insights = st.session_state["insights"]
    config = st.session_state["run_config"]

    ai_mode = "AI-classified" if settings.openrouter_configured else "Keyword-classified"
    source_mode = config["source"]
    st.success(
        f"**{len(df_processed)} conversations** analyzed | "
        f"Source: {source_mode} | {ai_mode} | {config['timestamp']}"
    )

    # Section 1: Overview
    render_overview_metrics(df_processed)
    st.divider()

    # Section 2: Source + Sentiment
    render_source_mix_and_sentiment(df_processed)
    st.divider()

    # Section 3: Brand intelligence
    render_brand_sentiment(df_processed, config["brands"])
    st.divider()

    # Section 3b: Brand correspondence map
    render_brand_correspondence_map(df_processed, config["brands"])
    st.divider()

    # Brand filter — applies to sections 4-7
    selected_brand = render_brand_filter(config["brands"])
    brand_context = build_brand_context(df_processed, selected_brand)

    # Section 4: Themes + Pain points
    render_themes_and_pain_points(df_processed, selected_brand)
    st.divider()

    # Section 5: Narratives
    render_narratives(insights, brand_context, selected_brand, config["brands"])
    st.divider()

    # Section 6: Executive summary
    render_executive_summary(insights, brand_context)
    st.divider()

    # Section 7: Recommendations
    render_recommendations(insights, brand_context)
    st.divider()

    # Section 8: Downloads
    render_download_section(df_raw, df_processed, insights, config)

else:
    # Welcome state
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""<div style="background:#f8f9fa; border-radius:8px; padding:20px;
            border-top:4px solid #1a1a2e; text-align:center;">
            <h3 style="color:#1a1a2e">🔍 Scrape</h3>
            <p>Pull consumer conversations from Reddit India and other platforms
            using Apify — or use built-in sample data to start immediately.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div style="background:#f8f9fa; border-radius:8px; padding:20px;
            border-top:4px solid #0984e3; text-align:center;">
            <h3 style="color:#1a1a2e">🧠 Classify</h3>
            <p>OpenRouter AI extracts sentiment, themes, pain points, emotional drivers,
            and business implications from every conversation.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""<div style="background:#f8f9fa; border-radius:8px; padding:20px;
            border-top:4px solid #00b894; text-align:center;">
            <h3 style="color:#1a1a2e">📊 Insight</h3>
            <p>Strategic recommendations written at the level of a senior consumer
            strategist — answering What, Why, and What Should the Brand Do.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "👈 **Configure your analysis in the sidebar and click Run Analysis.**\n\n"
        "Select keywords, brands, and data sources — then click **Run Analysis** to generate "
        "AI-powered consumer intelligence from Indian digital platforms."
    )
