"""
Dashboard Components — India Consumer Pulse AI

Stateless rendering functions. Each function receives data and renders
Streamlit UI elements. No business logic here — only display logic.
"""

from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Color palette ─────────────────────────────────────────────
COLORS = {
    "positive": "#00b894",
    "negative": "#e94560",
    "neutral":  "#636e72",
    "mixed":    "#fdcb6e",
    "navy":     "#1a1a2e",
    "accent":   "#e94560",
    "bg_card":  "#f8f9fa",
    "bg_blue":  "#eef2ff",
}

SENTIMENT_COLOR_MAP = {
    "positive": COLORS["positive"],
    "negative": COLORS["negative"],
    "neutral":  COLORS["neutral"],
    "mixed":    COLORS["mixed"],
}

BRAND_PALETTE = [
    "#1a1a2e", "#0984e3", "#6c5ce7", "#00b894",
    "#e17055", "#fdcb6e", "#a29bfe", "#fd79a8",
]


# ── Brand spotlight helpers ───────────────────────────────────

def build_brand_context(df: pd.DataFrame, brand_name: str) -> dict:
    """Compute quick stats for a single brand from filtered df."""
    if brand_name == "All Brands" or df.empty:
        return {}
    bdf = df[df["brand"] == brand_name] if "brand" in df.columns else df
    if bdf.empty:
        return {}

    sent_counts = bdf["sentiment"].value_counts().to_dict() if "sentiment" in bdf else {}
    dominant = max(sent_counts, key=sent_counts.get) if sent_counts else "N/A"
    top_themes = (
        bdf["theme"].value_counts().head(3).index.tolist() if "theme" in bdf else []
    )
    top_pains = (
        bdf["pain_point"].dropna().value_counts().head(2).index.tolist()
        if "pain_point" in bdf else []
    )
    sample = (
        bdf[bdf["sentiment"] == "negative"]["text"].head(1).values[0][:200]
        if "sentiment" in bdf and (bdf["sentiment"] == "negative").any()
        else (bdf["text"].head(1).values[0][:200] if "text" in bdf else "")
    )
    return {
        "brand": brand_name,
        "count": len(bdf),
        "sentiment_counts": sent_counts,
        "dominant_sentiment": dominant,
        "top_themes": top_themes,
        "top_pain_points": top_pains,
        "sample_voice": sample,
    }


def _render_brand_spotlight(ctx: dict) -> None:
    """Render a compact brand context card above filtered sections."""
    if not ctx:
        return
    dom = ctx.get("dominant_sentiment", "neutral")
    color = SENTIMENT_COLOR_MAP.get(dom, COLORS["neutral"])
    themes_str = " · ".join(ctx.get("top_themes", [])) or "—"
    pains_str = "; ".join(ctx.get("top_pain_points", [])) or "None detected"
    sample = ctx.get("sample_voice", "")

    st.markdown(
        f"""<div style="background:#fff8f0; border-left:4px solid {color};
        border-radius:6px; padding:14px 18px; margin-bottom:16px;">
        <strong style="color:{COLORS['navy']}; font-size:1.05em">
        🔍 Brand filter: {ctx['brand']}</strong>
        &nbsp;|&nbsp; {ctx['count']} conversations
        &nbsp;|&nbsp; Dominant sentiment:
        <span style="color:{color}; font-weight:600">{dom.capitalize()}</span>
        <br><span style="color:#636e72; font-size:0.9em">
        Top themes: <em>{themes_str}</em>
        </span><br>
        <span style="color:#636e72; font-size:0.9em">
        Key pain points: <em>{pains_str}</em>
        </span>
        {f'<br><span style="color:#636e72; font-size:0.88em; font-style:italic">Sample voice: "{sample}..."</span>' if sample else ""}
        </div>""",
        unsafe_allow_html=True,
    )


# ── Brand filter widget ───────────────────────────────────────

def render_brand_filter(brands: list[str], key: str = "brand_filter") -> str:
    """Render the brand filter selectbox. Returns selected brand name."""
    options = ["All Brands"] + (brands if brands else [])
    col1, col2 = st.columns([2, 5])
    with col1:
        selected = st.selectbox(
            "Filter by Brand",
            options=options,
            key=key,
            help="Filter themes, pain points, and AI insights by a specific brand.",
        )
    return selected


# ── Overview metrics ──────────────────────────────────────────

def render_overview_metrics(df: pd.DataFrame) -> None:
    total = len(df)
    sources = df["source"].nunique() if "source" in df.columns else 0
    brands = df[df["brand"] != "Other"]["brand"].nunique() if "brand" in df.columns else 0
    sentiment_label = "N/A"
    if "sentiment" in df.columns:
        sc = df["sentiment"].value_counts()
        sentiment_label = sc.index[0].capitalize() if len(sc) > 0 else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Conversations Analyzed", f"{total:,}")
    c2.metric("Data Sources", sources)
    c3.metric("Brands Tracked", brands)
    c4.metric("Dominant Sentiment", sentiment_label)


# ── Source mix + Sentiment split ──────────────────────────────

def render_source_mix_and_sentiment(df: pd.DataFrame) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Source Mix")
        if "source" in df.columns:
            src = df["source"].value_counts().reset_index()
            src.columns = ["source", "count"]
            fig = px.pie(
                src, values="count", names="source", hole=0.45,
                color_discrete_sequence=[COLORS["navy"], COLORS["accent"], "#0984e3", "#6c5ce7"],
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                              showlegend=True, height=260,
                              legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Reddit India drives high-intent, considered consumer tech conversation.")
        else:
            st.info("Source data not available.")

    with c2:
        st.subheader("Sentiment Breakdown")
        if "sentiment" in df.columns:
            sent = df["sentiment"].value_counts().reset_index()
            sent.columns = ["sentiment", "count"]
            fig = px.bar(
                sent, x="count", y="sentiment", orientation="h",
                color="sentiment", color_discrete_map=SENTIMENT_COLOR_MAP,
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                              showlegend=False, height=260,
                              xaxis_title="Conversations", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
            neg = df["sentiment"].eq("negative").sum()
            pos = df["sentiment"].eq("positive").sum()
            if neg > pos:
                st.caption(
                    f"Negative outweighs positive by {neg - pos} — investigate top pain points."
                )
            elif pos > neg:
                st.caption(
                    f"Positive leads — {pos} conversations show brand resonance. Amplify what works."
                )
            else:
                st.caption("Balanced sentiment — common in considered-purchase categories.")
        else:
            st.info("Run analysis to see sentiment breakdown.")


# ── Brand-wise sentiment ──────────────────────────────────────

def render_brand_sentiment(df: pd.DataFrame, brands: list[str]) -> None:
    st.subheader("Brand Intelligence — Sentiment by Brand")
    if "brand" not in df.columns or "sentiment" not in df.columns:
        st.info("Brand sentiment data not available.")
        return

    tracked = df[df["brand"].isin(brands)] if brands else df
    if tracked.empty:
        st.info("No data for selected brands.")
        return

    brand_sent = (
        tracked.groupby(["brand", "sentiment"]).size().reset_index(name="count")
    )
    fig = px.bar(
        brand_sent, x="brand", y="count", color="sentiment",
        barmode="group", color_discrete_map=SENTIMENT_COLOR_MAP,
        labels={"count": "Conversations", "brand": "Brand", "sentiment": "Sentiment"},
    )
    fig.update_layout(
        margin=dict(t=10, b=10), height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis_title="", yaxis_title="Conversation volume",
    )
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(min(len(brands), 3))
    for i, brand in enumerate(brands):
        bdf = tracked[tracked["brand"] == brand]
        if bdf.empty:
            continue
        sc = bdf["sentiment"].value_counts()
        dominant = sc.index[0] if len(sc) > 0 else "neutral"
        top_theme = (
            bdf["theme"].value_counts().index[0]
            if "theme" in bdf.columns and not bdf["theme"].empty else "—"
        )
        color = SENTIMENT_COLOR_MAP.get(dominant, COLORS["neutral"])
        with cols[i % len(cols)]:
            st.markdown(
                f"""<div style="border-left:4px solid {color}; padding:10px 14px;
                background:{COLORS['bg_card']}; border-radius:4px; margin-bottom:10px;">
                <strong>{brand}</strong><br>
                <span style="color:{color}">● {dominant.capitalize()}</span> | {len(bdf)} convs<br>
                <span style="color:#636e72; font-size:0.85em">Top: <em>{top_theme}</em></span>
                </div>""",
                unsafe_allow_html=True,
            )

    st.caption(
        "Brand sentiment in competitive context — relative positioning signals within "
        "Indian consumer tech discourse."
    )


# ── Brand Correspondence Map ──────────────────────────────────

def render_brand_correspondence_map(df: pd.DataFrame, brands: list[str]) -> None:
    """
    Correspondence-analysis-style brand × theme map.
    Brands are positioned near their most associated themes using SVD.
    """
    st.subheader("Brand Association Map")
    st.caption(
        "Brands positioned near the themes they are most associated with in consumer conversation. "
        "Brands close to each other share similar theme profiles."
    )

    if "brand" not in df.columns or "theme" not in df.columns:
        st.info("Need brand and theme data. Run AI classification first.")
        return

    tracked = df[df["brand"].isin(brands)] if brands else df
    tracked = tracked[tracked["brand"] != "Other"]

    if tracked["brand"].nunique() < 2:
        st.info("Need at least 2 brands with data for the association map.")
        return

    contingency = pd.crosstab(tracked["brand"], tracked["theme"])
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        st.info("Need at least 2 brands and 2 themes for the association map.")
        return

    # Limit to top 8 themes by volume before SVD — reduces clutter without losing signal
    _TOP_THEMES = 8
    if contingency.shape[1] > _TOP_THEMES:
        top_cols = contingency.sum(axis=0).nlargest(_TOP_THEMES).index
        contingency = contingency[top_cols]

    # ── Correspondence Analysis via SVD ──────────────────────
    X = contingency.values.astype(float)
    grand_n = X.sum()
    P = X / grand_n
    row_mass = P.sum(axis=1)          # brand marginals
    col_mass = P.sum(axis=0)          # theme marginals

    Dr_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(row_mass, 1e-10)))
    Dc_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(col_mass, 1e-10)))

    # Standardised residuals
    S = Dr_inv_sqrt @ (P - np.outer(row_mass, col_mass)) @ Dc_inv_sqrt
    U, sigma, Vt = np.linalg.svd(S, full_matrices=False)

    # Principal coordinates
    brand_coords = Dr_inv_sqrt @ U[:, :2] * sigma[:2]   # shape (n_brands, 2)
    theme_coords = Dc_inv_sqrt @ Vt[:2].T * sigma[:2]   # shape (n_themes, 2)

    brand_names = contingency.index.tolist()
    theme_names = contingency.columns.tolist()
    theme_totals = contingency.values.sum(axis=0)
    brand_row_totals = contingency.values.sum(axis=1)

    # ── Compute dominant sentiment per theme ─────────────────────
    _SENT_COLOR = {
        "negative": "#e94560",
        "positive": "#00b894",
        "mixed":    "#fdcb6e",
        "neutral":  "#636e72",
    }
    theme_sentiment_map: dict[str, str] = {}
    if "sentiment" in tracked.columns:
        for theme in theme_names:
            tdf = tracked[tracked["theme"] == theme]
            if not tdf.empty:
                theme_sentiment_map[theme] = tdf["sentiment"].value_counts().index[0]

    # ── Build figure ──────────────────────────────────────────
    fig = go.Figure()

    fig.add_hline(y=0, line_width=0.8, line_dash="dot", line_color="#dfe6e9")
    fig.add_vline(x=0, line_width=0.8, line_dash="dot", line_color="#dfe6e9")

    brand_colors_list = BRAND_PALETTE

    # ── Theme markers + sentiment-colored labels ─────────────────
    # One annotation per theme so each label can have its own color.
    # Diamond color also reflects sentiment — red = negative risk,
    # green = positive strength, amber = mixed, grey = neutral.
    _textpos_cycle = ["top center", "bottom center", "top right", "bottom left",
                      "top left", "bottom right", "middle right", "middle left"]

    for j, theme in enumerate(theme_names):
        sent = theme_sentiment_map.get(theme, "neutral")
        color = _SENT_COLOR[sent]
        size = 10 + int(theme_totals[j] / max(theme_totals) * 8)

        fig.add_trace(go.Scatter(
            x=[theme_coords[j, 0]],
            y=[theme_coords[j, 1]],
            mode="markers",
            marker=dict(
                size=size, color=color, symbol="diamond",
                opacity=0.75,
                line=dict(color="white", width=1.2),
            ),
            showlegend=False,
            hovertemplate=(
                f"<b>{theme}</b><br>"
                f"Sentiment: {sent}<br>"
                f"Mentions: {int(theme_totals[j])}<extra></extra>"
            ),
        ))

        # Annotation label — color signals sentiment, background keeps it readable
        fig.add_annotation(
            x=theme_coords[j, 0],
            y=theme_coords[j, 1],
            text=f"<b>{theme}</b>" if sent == "negative" else theme,
            font=dict(size=9, color=color),
            showarrow=False,
            yshift=15,
            bgcolor="rgba(255,255,255,0.82)",
            bordercolor=color,
            borderwidth=1,
            borderpad=3,
        )

    # ── Brand markers ────────────────────────────────────────────
    for i, brand in enumerate(brand_names):
        bdf = tracked[tracked["brand"] == brand]
        dom_sent = (
            bdf["sentiment"].value_counts().index[0]
            if "sentiment" in bdf.columns and not bdf.empty else "neutral"
        )
        n_convs = int(brand_row_totals[i])
        top_theme = contingency.iloc[i].idxmax()
        marker_size = 18 + int(n_convs / max(brand_row_totals) * 16)
        color = brand_colors_list[i % len(brand_colors_list)]

        fig.add_trace(go.Scatter(
            x=[brand_coords[i, 0]],
            y=[brand_coords[i, 1]],
            mode="markers+text",
            marker=dict(
                size=marker_size, color=color, symbol="circle",
                line=dict(color="white", width=2.5),
                opacity=0.9,
            ),
            text=[f"<b>{brand}</b>"],
            textposition="top center",
            textfont=dict(size=12, color=COLORS["navy"]),
            name=brand,
            hovertemplate=(
                f"<b>{brand}</b><br>"
                f"Conversations: {n_convs}<br>"
                f"Top theme: {top_theme}<br>"
                f"Dominant sentiment: {dom_sent}<extra></extra>"
            ),
        ))

    # Variance explained
    if len(sigma) >= 2:
        total_var = (sigma ** 2).sum()
        d1_pct = f"{sigma[0]**2 / total_var * 100:.0f}%" if total_var > 0 else ""
        d2_pct = f"{sigma[1]**2 / total_var * 100:.0f}%" if total_var > 0 else ""
    else:
        d1_pct, d2_pct = "", ""

    fig.update_layout(
        xaxis=dict(
            title=f"Dimension 1 ({d1_pct} variance)",
            zeroline=False, showgrid=False,
        ),
        yaxis=dict(
            title=f"Dimension 2 ({d2_pct} variance)",
            zeroline=False, showgrid=False,
        ),
        height=560,
        margin=dict(t=20, b=20, l=20, r=20),
        plot_bgcolor="#fafafa",
        paper_bgcolor="white",
        showlegend=True,
        legend=dict(
            title="Brands", orientation="v", x=1.01,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#dfe6e9", borderwidth=1,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Inline legend for theme sentiment colors
    st.markdown(
        "<div style='font-size:0.85em; color:#636e72; margin-top:-8px; margin-bottom:4px;'>"
        "<span style='color:#e94560'>◆ <b>Red</b> = negative theme (brand risk)</span>"
        "&nbsp;&nbsp;"
        "<span style='color:#00b894'>◆ <b>Green</b> = positive theme (brand strength)</span>"
        "&nbsp;&nbsp;"
        "<span style='color:#fdcb6e'>◆ <b>Amber</b> = mixed</span>"
        "&nbsp;&nbsp;"
        "<span style='color:#636e72'>◆ <b>Grey</b> = neutral</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "**How to read:** Brands (circles) positioned near a theme (diamond) are most associated "
        "with it in consumer conversation. Theme color shows whether that association is a "
        "risk (red), strength (green), or neutral signal (grey). Hover any theme for mention count."
    )

    # ── Heatmap alternative view ──────────────────────────────
    with st.expander("Brand × Theme Heatmap (detailed view)"):
        top_themes = (
            contingency.sum(axis=0).nlargest(10).index.tolist()
        )
        heat_data = contingency[top_themes] if len(top_themes) > 0 else contingency
        fig_heat = px.imshow(
            heat_data,
            color_continuous_scale=[[0, "#f8f9fa"], [0.3, "#a29bfe"], [1, COLORS["navy"]]],
            labels=dict(x="Theme", y="Brand", color="Conversations"),
            aspect="auto",
            text_auto=True,
        )
        fig_heat.update_layout(
            height=max(250, len(brand_names) * 60),
            margin=dict(t=10, b=10),
            coloraxis_showscale=False,
        )
        fig_heat.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.caption(
            "Cell value = number of conversations associating that brand with that theme. "
            "Darker = stronger association."
        )


# ── Top themes + Pain points ──────────────────────────────────

def render_themes_and_pain_points(
    df: pd.DataFrame, selected_brand: str = "All Brands"
) -> None:
    # Apply brand filter
    filtered = (
        df[df["brand"] == selected_brand]
        if selected_brand != "All Brands" and "brand" in df.columns
        else df
    )

    ctx = build_brand_context(df, selected_brand)
    if ctx:
        _render_brand_spotlight(ctx)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top Conversation Themes")
        if selected_brand != "All Brands":
            st.caption(f"Showing themes for **{selected_brand}** only")
        if "theme" in filtered.columns and not filtered.empty:
            themes = filtered["theme"].value_counts().head(8).reset_index()
            themes.columns = ["theme", "count"]
            fig = px.bar(
                themes, x="count", y="theme", orientation="h",
                color="count",
                color_continuous_scale=[[0, "#b2bec3"], [1, COLORS["navy"]]],
            )
            fig.update_layout(
                margin=dict(t=10, b=10), height=320,
                showlegend=False, coloraxis_showscale=False,
                xaxis_title="Conversations", yaxis_title="",
            )
            fig.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "High-volume themes with strong negative sentiment = highest priority "
                "brand attention areas."
            )
        else:
            st.info("Theme data not available — run AI classification.")

    with c2:
        st.subheader("Consumer Pain Points")
        if selected_brand != "All Brands":
            st.caption(f"Showing pain points for **{selected_brand}** only")
        if "pain_point" in filtered.columns and not filtered.empty:
            pp = filtered["pain_point"].dropna()
            if pp.empty:
                st.info("No pain points detected in this dataset.")
            else:
                pp_counts = pp.value_counts().head(6)
                max_count = pp_counts.max()
                for pain, count in pp_counts.items():
                    bar_pct = max(int(count / max(max_count, 1) * 100), 8)
                    st.markdown(
                        f"""<div style="margin-bottom:12px;">
                        <span style="font-weight:600; color:{COLORS['navy']}">{pain}</span>
                        <br>
                        <div style="background:#f0f0f0; border-radius:4px; height:8px; margin-top:4px;">
                          <div style="background:{COLORS['accent']}; width:{bar_pct}%;
                               height:8px; border-radius:4px;"></div>
                        </div>
                        <span style="color:#636e72; font-size:0.82em">
                          {count} mention{'s' if count != 1 else ''}
                        </span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                st.caption(
                    "Pain points = latent needs waiting for a brand solution. "
                    "Highest-volume items are the strongest product/comm opportunities."
                )
        else:
            st.info("Run AI classification to detect pain points.")


# ── Narratives ────────────────────────────────────────────────

def render_narratives(
    insights: dict,
    brand_context: Optional[dict] = None,
    selected_brand: str = "All Brands",
    brands: Optional[list] = None,
) -> None:
    st.subheader("Dominant Consumer Narratives")
    st.caption("The 3 most strategically significant stories emerging from this data.")

    # Inline brand filter — controls the 'What should [brand] do?' row
    brand_options = ["All Brands"] + (brands or [])
    col_filter, col_hint = st.columns([2, 5])
    with col_filter:
        active_brand = st.selectbox(
            "Brand lens",
            options=brand_options,
            index=brand_options.index(selected_brand) if selected_brand in brand_options else 0,
            key="narrative_brand_filter",
            help="Switch brand to see a tailored 'What should [brand] do?' action for each narrative.",
        )
    with col_hint:
        if active_brand != "All Brands":
            st.markdown(
                f"<div style='padding-top:28px; color:#636e72; font-size:0.88em;'>"
                f"Showing <strong>{active_brand}</strong>-specific strategic actions. "
                f"Trend, driver, and implication reflect the full category.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='padding-top:28px; color:#636e72; font-size:0.88em;'>"
                "Select a brand to see tailored strategic actions per narrative.</div>",
                unsafe_allow_html=True,
            )

    # Update brand context to match the inline selection
    if active_brand != selected_brand and active_brand != "All Brands":
        brand_context = build_brand_context(
            insights.get("_df", pd.DataFrame()), active_brand
        )

    if brand_context and active_brand != "All Brands":
        _render_brand_spotlight(brand_context)

    narratives = insights.get("dominant_narratives", [])
    if not narratives:
        st.info("Narratives not generated.")
        return

    brand_specific = active_brand != "All Brands"
    action_label = (
        f"What should {active_brand} do?" if brand_specific else "What should brands do?"
    )

    _INSIGHT_ROWS = [
        ("What is happening?",   "trend",                "#1a1a2e"),
        ("Why is it happening?", "consumer_driver",      "#0984e3"),
        ("Why does it matter?",  "business_implication", "#6c5ce7"),
        (action_label,           "strategic_action",     "#00b894"),
    ]
    palette = [COLORS["navy"], "#0984e3", "#6c5ce7"]

    for i, narrative in enumerate(narratives):
        color = palette[i % len(palette)]

        if isinstance(narrative, dict):
            rows_html = ""
            for label, key, row_color in _INSIGHT_ROWS:
                if key == "strategic_action" and brand_specific:
                    text = narrative.get("brand_actions", {}).get(
                        active_brand,
                        narrative.get("strategic_action", ""),
                    )
                else:
                    text = narrative.get(key, "")

                rows_html += f"""<tr>
                  <td style="width:210px; padding:8px 12px; vertical-align:top;
                       background:{COLORS['bg_card']}; border-right:1px solid #e0e0e0;">
                    <span style="font-size:0.78em; font-weight:700; color:{row_color};
                         text-transform:uppercase; letter-spacing:0.05em;">{label}</span>
                  </td>
                  <td style="padding:8px 14px; vertical-align:top; color:#2d3436;
                       line-height:1.7; font-size:0.97em;">
                    {text}
                  </td>
                </tr>"""

            st.markdown(
                f"""<div style="border:1px solid #e0e0e0; border-top:4px solid {color};
                border-radius:6px; margin-bottom:18px; overflow:hidden;">
                  <div style="background:{color}; padding:8px 14px;">
                    <strong style="color:white; font-size:0.95em">Narrative {i + 1}</strong>
                  </div>
                  <table style="width:100%; border-collapse:collapse;">{rows_html}</table>
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""<div style="border-left:4px solid {color}; padding:14px 18px;
                background:{COLORS['bg_card']}; border-radius:4px; margin-bottom:14px;
                line-height:1.75;">
                <strong style="color:{color}">Narrative {i + 1}</strong><br>
                {narrative}
                </div>""",
                unsafe_allow_html=True,
            )


# ── Executive summary ─────────────────────────────────────────

def render_executive_summary(
    insights: dict,
    brand_context: Optional[dict] = None,
) -> None:
    st.subheader("AI Executive Summary")
    st.caption(
        "Strategic interpretation written for a CMO — not a data analyst."
    )

    if brand_context:
        _render_brand_spotlight(brand_context)
        st.markdown(
            "<span style='color:#636e72; font-size:0.88em'>"
            "ℹ️ AI summary reflects the full dataset. "
            "Brand spotlight above provides brand-specific context.</span>",
            unsafe_allow_html=True,
        )

    summary = insights.get("executive_summary", "")
    if not summary:
        st.info("Executive summary not generated.")
        return

    st.markdown(
        f"""<div style="background:{COLORS['bg_blue']}; border-radius:8px;
        padding:20px 24px; line-height:1.85; color:{COLORS['navy']}; font-size:1.02em;">
        {summary.replace(chr(10), "<br>")}
        </div>""",
        unsafe_allow_html=True,
    )


# ── Strategic recommendations ─────────────────────────────────

def render_recommendations(
    insights: dict,
    brand_context: Optional[dict] = None,
) -> None:
    st.subheader("Strategic Recommendations")
    st.caption(
        "India-specific brand actions grounded in consumer signals. "
        "Each answers: What? Why? How? Priority?"
    )

    if brand_context:
        _render_brand_spotlight(brand_context)
        brand = brand_context.get("brand", "")
        st.markdown(
            f"<span style='color:#636e72; font-size:0.88em'>"
            f"ℹ️ Showing all recommendations. "
            f"Prioritise those relevant to <strong>{brand}</strong>'s top themes and pain points above.</span>",
            unsafe_allow_html=True,
        )

    recs = insights.get("strategic_recommendations", [])
    if not recs:
        st.info("Recommendations not generated.")
        return

    priority_colors = {
        "High": COLORS["accent"],
        "Medium": "#fdcb6e",
        "Low": COLORS["neutral"],
    }

    for i, rec in enumerate(recs, 1):
        if not isinstance(rec, dict):
            st.markdown(f"**{i}.** {rec}")
            continue
        priority = rec.get("priority", "Medium")
        p_color = priority_colors.get(priority, COLORS["neutral"])
        st.markdown(
            f"""<div style="background:{COLORS['bg_card']}; border-radius:8px;
            padding:16px 20px; margin-bottom:12px; border-top:3px solid {p_color};">
            <div style="display:flex; justify-content:space-between; align-items:center;
                 margin-bottom:8px;">
              <strong style="font-size:1.05em; color:{COLORS['navy']}">
                {i}. {rec.get('action', '')}
              </strong>
              <span style="background:{p_color}; color:white; padding:2px 10px;
                   border-radius:12px; font-size:0.8em; font-weight:600;">
                {priority}
              </span>
            </div>
            <p style="margin:4px 0; color:#2d3436;">
              <strong>Why:</strong> {rec.get('rationale', '')}
            </p>
            <p style="margin:4px 0; color:#2d3436;">
              <strong>How:</strong> {rec.get('how', '')}
            </p>
            </div>""",
            unsafe_allow_html=True,
        )


# ── Download section ──────────────────────────────────────────

def render_download_section(
    df_raw: pd.DataFrame,
    df_processed: pd.DataFrame,
    insights: dict,
    config: dict,
) -> None:
    st.subheader("Download Intelligence Package")
    st.caption("Export for sharing with your team or clients.")

    c1, c2, c3 = st.columns(3)

    from datetime import date as _date
    _today = _date.today().strftime("%Y-%m-%d")

    with c1:
        st.download_button(
            label="Raw Data (CSV)",
            data=df_raw.to_csv(index=False).encode("utf-8"),
            file_name=f"consumer_pulse_raw_{_today}.csv",
            mime="text/csv",
        )
        st.caption("All scraped conversations — unclassified")

    with c2:
        st.download_button(
            label="Classified Data (CSV)",
            data=df_processed.to_csv(index=False).encode("utf-8"),
            file_name=f"consumer_pulse_classified_{_today}.csv",
            mime="text/csv",
        )
        st.caption("Conversations with AI classification added")

    with c3:
        try:
            from insights.generator import generate_report_pdf
            _cache_key = f"pdf_{config.get('timestamp', '')}"
            if _cache_key not in st.session_state:
                st.session_state[_cache_key] = generate_report_pdf(
                    df_raw, df_processed, insights, config
                )
            pdf_bytes = st.session_state[_cache_key]
            st.download_button(
                label="Intelligence Report (PDF)",
                data=pdf_bytes,
                file_name=f"india_consumer_pulse_{_today}.pdf",
                mime="application/pdf",
            )
            st.caption("Full strategic report — share directly with your team or clients")
        except Exception as e:
            st.warning(f"PDF export unavailable: {e}")
