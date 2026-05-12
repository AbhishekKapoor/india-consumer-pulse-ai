"""
Insight Generator — India Consumer Pulse AI

Takes a classified DataFrame and generates:
- Executive summary (AI, strategic prose)
- Dominant consumer narratives (AI, 3 narratives)
- Strategic recommendations (AI, 4 recommendations)

All AI calls route through ai/openrouter_client.py.
Falls back to data-driven template insights when OpenRouter is unavailable.
"""

import io
import logging
import unicodedata
from collections import Counter
from typing import Optional

import pandas as pd

from ai.openrouter_client import get_client
from config.settings import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a senior consumer insights strategist and AI-powered business intelligence analyst.

Your role is NOT to summarize data mechanically.

Your role is to transform consumer conversations, reviews, comments, social discussions, and market \
signals into strategic consumer insights, emerging narratives, business implications, and actionable \
brand recommendations.

You must think like a senior market researcher, consumer psychologist, strategy consultant, brand \
advisor, and CMO intelligence partner.

Your output should sound strategic, concise, executive-ready, insight-led, business-focused, human, \
and consulting-style. Avoid sounding robotic, academic, or overly technical.

---

CORE ANALYSIS FRAMEWORK

For every insight, always answer these 4 questions:

1. What is happening?
   Identify the observable trend, shift, pattern, or signal.

2. Why is it happening?
   Identify the consumer driver, emotional trigger, behavioral shift, cultural movement, or unmet need.

3. Why does it matter?
   Explain the business implication, market impact, category risk/opportunity, or strategic relevance.

4. What should brands do?
   Provide a practical strategic recommendation, positioning idea, communication direction, product \
implication, or action plan.

Never skip any of these four layers.

---

INSIGHT QUALITY RULES

Do NOT generate generic summaries.
  Bad:  "Consumers are talking about battery life."
  Good: "Battery life is increasingly becoming a productivity trust signal rather than a functional \
feature among Indian premium laptop buyers."

Focus on strategic interpretation — always go beyond sentiment:
  - motivations and anxieties
  - aspirations and identity signals
  - emotional tradeoffs and cultural shifts
  - status signaling and value perception
  - trust dynamics and premiumization patterns
  - convenience expectations and behavioral change

Sound like a senior strategist writing for CMOs, brand managers, strategy teams, and consumer \
insight heads. Every insight must lead to a recommendation, business opportunity, communication \
implication, or positioning direction.

Identify emerging narratives: shifting aspirations, changing expectations, emotional contradictions, \
identity-based consumption, category fatigue, trust shifts, AI adoption anxieties.

---

INDIA MARKET CONTEXT — ALWAYS APPLY

- Price tiers: <₹10K (mass), ₹10K–25K (mid), ₹25K–50K (premium), >₹50K (ultra-premium). \
Sentiment is often anchored to tier, not absolute price.
- EMI culture: a significant share of consumer tech decisions are EMI-driven; treat EMI-related \
sentiment as a distinct signal layer, not generic price sensitivity.
- Service infrastructure: after-sales quality varies sharply outside tier-1 cities; this is a \
genuine financial risk for EMI-committed consumers.
- Trust hierarchy: peer recommendations > influencer reviews > brand claims > advertising. \
Weight peer-generated content highest.
- Aspirational vs. practical split: distinguish desire-language (what consumers want) from \
purchase-intent-language (what they will actually buy).
- Festival buying: sentiment and purchase intent spike around Diwali, Republic Day, and Independence \
Day sales — flag sale-period signals separately.
- Hinglish discourse: consumers mix English and Hindi naturally; read sentiment and irony accordingly.
- Platform weighting: Reddit India and Play Store reviews carry the highest intent signal; \
Twitter/X is real-time but noisy.

Always name specific consumer segments — never just "Indian consumers". \
Example: "urban Indian mid-market laptop buyers upgrading from a 5-year-old device"."""


# ── Public API ────────────────────────────────────────────────

def generate_insights(
    df: pd.DataFrame,
    category: str,
    brands: list[str],
    keywords: list[str],
) -> dict:
    """Return dict with executive_summary, dominant_narratives, strategic_recommendations."""
    summary = _build_data_summary(df, brands)
    client = get_client()
    logger.info(
        f"Generating insights: {summary.get('total_records', 0)} records, "
        f"{len(brands)} brands, model={settings.OPENROUTER_SUMMARY_MODEL}, "
        f"max_tokens={settings.MAX_TOKENS_SUMMARY}"
    )

    if client.is_available:
        exec_summary = _generate_executive_summary(summary, category, client)
        logger.info("Executive summary: %s", "AI" if exec_summary and exec_summary != _fallback_summary(summary, category) else "fallback")
        narratives = _generate_narratives(summary, category, client)
        logger.info("Narratives: %s", "AI" if narratives and narratives != _fallback_narratives(summary) else "fallback")
        recommendations = _generate_recommendations(summary, category, brands, client)
        logger.info("Recommendations: %s", "AI" if recommendations and recommendations != _fallback_recommendations(summary) else "fallback")
    else:
        logger.warning("OpenRouter unavailable — using template insights")
        exec_summary = _fallback_summary(summary, category)
        narratives = _fallback_narratives(summary)
        recommendations = _fallback_recommendations(summary)

    logger.info("Insight generation complete")
    return {
        "executive_summary": exec_summary,
        "dominant_narratives": narratives,
        "strategic_recommendations": recommendations,
        "data_summary": summary,
    }


def generate_report_markdown(
    df_raw: pd.DataFrame,
    df_processed: pd.DataFrame,
    insights: dict,
    config: dict,
) -> str:
    """Build a downloadable markdown intelligence report."""
    summary = insights.get("data_summary", {})
    lines = [
        "# India Consumer Pulse AI — Intelligence Report",
        "",
        f"**Category:** {config.get('category', 'Consumer Tech India')}",
        f"**Analysis Date:** {config.get('timestamp', '')}",
        f"**Conversations Analyzed:** {len(df_processed)}",
        f"**Keywords:** {', '.join(config.get('keywords', []))}",
        f"**Brands Tracked:** {', '.join(config.get('brands', []))}",
        f"**Data Source:** {config.get('source', '')}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        insights.get("executive_summary", ""),
        "",
        "---",
        "",
        "## Dominant Consumer Narratives",
        "",
    ]
    for i, n in enumerate(insights.get("dominant_narratives", []), 1):
        lines += [f"### Narrative {i}", ""]
        if isinstance(n, dict):
            lines += [
                f"**What is happening:** {n.get('trend', '')}",
                "",
                f"**Why is it happening:** {n.get('consumer_driver', '')}",
                "",
                f"**Why does it matter:** {n.get('business_implication', '')}",
                "",
                f"**What should brands do:** {n.get('strategic_action', '')}",
                "",
            ]
        else:
            lines += [str(n), ""]

    lines += ["---", "", "## Brand Intelligence", ""]
    for brand, data in summary.get("brand_sentiment", {}).items():
        dominant = max(data, key=data.get) if data else "neutral"
        lines.append(f"- **{brand}**: Dominant sentiment — {dominant} | Mentions: {sum(data.values())}")

    lines += [
        "",
        "---",
        "",
        "## Top Themes",
        "",
    ]
    for theme, count in list(summary.get("top_themes", {}).items())[:6]:
        lines.append(f"- {theme.title()} ({count} mentions)")

    lines += ["", "---", "", "## Consumer Pain Points", ""]
    for pp, count in list(summary.get("top_pain_points", {}).items())[:5]:
        lines.append(f"- **{pp}** ({count} mentions)")

    lines += ["", "---", "", "## Strategic Recommendations", ""]
    for i, rec in enumerate(insights.get("strategic_recommendations", []), 1):
        if isinstance(rec, dict):
            lines += [
                f"### Recommendation {i}: {rec.get('action', '')}",
                "",
                f"**Why:** {rec.get('rationale', '')}",
                "",
                f"**How:** {rec.get('how', '')}",
                "",
                f"**Priority:** {rec.get('priority', 'Medium')}",
                "",
            ]
        else:
            lines += [f"{i}. {rec}", ""]

    lines += [
        "---",
        "",
        "*Report generated by India Consumer Pulse AI*",
        "*Data reflects Indian digital consumer conversations*",
        "*For strategic use by brand managers and marketing leadership*",
    ]

    return "\n".join(lines)


# ── PDF report generator ──────────────────────────────────────

def generate_report_pdf(
    df_raw: pd.DataFrame,
    df_processed: pd.DataFrame,
    insights: dict,
    config: dict,
) -> bytes:
    """Build a professionally formatted PDF intelligence report. Returns bytes."""
    from fpdf import FPDF

    summary = insights.get("data_summary", {})

    # ── colour constants ──────────────────────────────────
    NAVY   = (26, 26, 46)
    BLUE   = (9, 132, 227)
    GREEN  = (0, 184, 148)
    RED    = (233, 69, 96)
    GREY   = (99, 110, 114)
    LGREY  = (248, 249, 250)
    WHITE  = (255, 255, 255)
    ORANGE = (253, 203, 110)

    SENTIMENT_COLOR = {
        "positive": GREEN, "negative": RED,
        "mixed": ORANGE,   "neutral": GREY,
    }

    _UNICODE_MAP = {
        "—": "--", "–": "-", "‒": "-",
        "‘": "'",  "’": "'", "“": '"', "”": '"',
        "…": "...", " ": " ", "•": "*",
        "₹": "Rs.", "�": "?", "→": "->",
        "←": "<-",  "•": "-", "·": ".",
    }

    def _safe(text: str) -> str:
        """Translate common Unicode chars and strip anything outside latin-1."""
        if not isinstance(text, str):
            text = str(text)
        for ch, rep in _UNICODE_MAP.items():
            text = text.replace(ch, rep)
        text = unicodedata.normalize("NFKD", text)
        return text.encode("latin-1", "replace").decode("latin-1")

    # ── PDF class ─────────────────────────────────────────
    class ReportPDF(FPDF):
        def header(self):
            if self.page_no() == 1:
                return
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*NAVY)
            self.cell(0, 6, "INDIA CONSUMER PULSE AI  |  Confidential Intelligence Report", align="L")
            self.set_draw_color(*NAVY)
            self.set_line_width(0.3)
            self.line(10, self.get_y() + 6, 200, self.get_y() + 6)
            self.ln(8)

        def footer(self):
            self.set_y(-14)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GREY)
            self.cell(0, 6, f"Page {self.page_no()}  |  India Consumer Pulse AI  |  Prepared by Abhishek Kapoor  |  For strategic use only", align="C")
            # footer defined before _safe is in scope — strings are ASCII-safe already

        def section_title(self, title: str):
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(*NAVY)
            self.set_fill_color(*LGREY)
            self.cell(0, 9, _safe(title), fill=True, ln=True)
            self.set_draw_color(*BLUE)
            self.set_line_width(0.8)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

        def body_text(self, text: str, indent: int = 0):
            self.set_font("Helvetica", "", 10)
            self.set_text_color(40, 40, 40)
            x = 10 + indent
            self.set_x(x)
            self.multi_cell(190 - indent, 5.5, _safe(text))
            self.ln(1)

        def kv_row(self, label: str, value: str, label_w: int = 55):
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*NAVY)
            self.set_x(10)
            self.cell(label_w, 6, _safe(label))
            self.set_font("Helvetica", "", 10)
            self.set_text_color(40, 40, 40)
            self.multi_cell(190 - label_w, 6, _safe(value))

        def colored_badge(self, text: str, color: tuple):
            self.set_font("Helvetica", "B", 9)
            self.set_fill_color(*color)
            self.set_text_color(*WHITE)
            self.cell(28, 6, _safe(text.upper()), fill=True, align="C")

        def bar(self, label: str, count: int, max_count: int, color: tuple = NAVY):
            bar_w = max(4, int((count / max(max_count, 1)) * 90))
            self.set_x(10)   # anchor every row to left margin — prevents drift
            self.set_font("Helvetica", "", 9)
            self.set_text_color(40, 40, 40)
            self.cell(70, 5.5, _safe(label[:38]))
            self.set_fill_color(*color)
            self.cell(bar_w, 5.5, "", fill=True)
            self.set_fill_color(*LGREY)
            self.cell(90 - bar_w, 5.5, "", fill=True)
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*NAVY)
            self.cell(20, 5.5, str(count), align="R", ln=True)
            self.ln(0.5)

    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    # ── COVER PAGE ────────────────────────────────────────
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, "F")

    pdf.set_y(60)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, "INDIA CONSUMER", align="C", ln=True)
    pdf.cell(0, 14, "PULSE AI", align="C", ln=True)

    pdf.set_y(105)
    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(1)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())

    pdf.ln(8)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(200, 210, 220)
    pdf.cell(0, 8, "Strategic Consumer Intelligence Report", align="C", ln=True)

    pdf.ln(20)
    cat = config.get("category", "Consumer Tech India")
    ts  = config.get("timestamp", "")
    src = config.get("source", "")
    d_from = config.get("date_from", "")
    d_to   = config.get("date_to", "")

    for label, value in [
        ("Category", cat),
        ("Analysis Date", ts),
        ("Data Sources", src),
        ("Period", f"{d_from} to {d_to}" if d_from else ""),
        ("Conversations", str(len(df_processed))),
        ("Brands Tracked", ", ".join(config.get("brands", []))),
    ]:
        if not value:
            continue
        y_now = pdf.get_y()
        pdf.set_xy(10, y_now)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*ORANGE)
        pdf.cell(55, 7, _safe(label + ":"), align="R")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*WHITE)
        pdf.multi_cell(130, 7, _safe(value))

    pdf.set_y(258)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*ORANGE)
    pdf.cell(0, 6, "Prepared by: Abhishek Kapoor", align="C", ln=True)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 140, 160)
    pdf.cell(0, 6, "India Consumer Pulse AI", align="C", ln=True)
    pdf.cell(0, 5, "Confidential - For strategic use by brand managers and marketing leadership", align="C", ln=True)

    # ── PAGE 2+ CONTENT ───────────────────────────────────
    pdf.add_page()

    # 1. Snapshot metrics
    pdf.section_title("01  Performance Snapshot")
    sc = summary.get("sentiment_counts", {})
    total = len(df_processed)
    dom_sent = max(sc, key=sc.get) if sc else "N/A"
    dom_color = SENTIMENT_COLOR.get(dom_sent, GREY)

    c_data = [
        ("Conversations Analyzed", str(total)),
        ("Dominant Sentiment", dom_sent.capitalize()),
        ("Brands Tracked", str(len(summary.get("brand_sentiment", {})))),
        ("Data Sources", str(df_processed["source"].nunique() if "source" in df_processed.columns else 1)),
    ]
    col_w = 47
    for i, (lbl, val) in enumerate(c_data):
        x = 10 + (i % 4) * col_w
        y_top = pdf.get_y()
        pdf.set_xy(x, y_top)
        pdf.set_fill_color(*LGREY)
        pdf.set_draw_color(*NAVY)
        pdf.set_line_width(0.3)
        pdf.rect(x, y_top, col_w - 2, 18, "FD")
        pdf.set_xy(x + 1, y_top + 2)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*GREY)
        pdf.cell(col_w - 4, 5, _safe(lbl))
        pdf.set_xy(x + 1, y_top + 8)
        pdf.set_font("Helvetica", "B", 13)
        color = dom_color if lbl == "Dominant Sentiment" else NAVY
        pdf.set_text_color(*color)
        pdf.cell(col_w - 4, 7, _safe(val))
    pdf.ln(22)

    # Sentiment breakdown
    if sc:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 6, "Sentiment Breakdown", ln=True)
        pdf.ln(1)
        max_s = max(sc.values())
        for sent, cnt in sorted(sc.items(), key=lambda x: -x[1]):
            pdf.bar(sent.capitalize(), cnt, max_s, SENTIMENT_COLOR.get(sent, GREY))
    pdf.ln(4)

    # 2. Executive Summary
    pdf.section_title("02  Executive Summary")
    exec_sum = insights.get("executive_summary", "")
    pdf.body_text(exec_sum)
    pdf.ln(3)

    # 3. Brand Intelligence
    pdf.section_title("03  Brand Intelligence")
    brand_sent = summary.get("brand_sentiment", {})
    if brand_sent:
        # Table header
        pdf.set_fill_color(*NAVY)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(50, 7, "Brand", fill=True)
        pdf.cell(30, 7, "Mentions", fill=True, align="C")
        pdf.cell(35, 7, "Dominant Sentiment", fill=True, align="C")
        pdf.cell(75, 7, "Sentiment Split", fill=True)
        pdf.ln()
        pdf.set_font("Helvetica", "", 9)
        toggle = False
        for brand, sent_dict in sorted(brand_sent.items(), key=lambda x: -sum(x[1].values())):
            mentions = sum(sent_dict.values())
            dom = max(sent_dict, key=sent_dict.get) if sent_dict else "N/A"
            dom_c = SENTIMENT_COLOR.get(dom, GREY)
            split_parts = [f"{s.capitalize()}: {c}" for s, c in sorted(sent_dict.items(), key=lambda x: -x[1])]
            split_str = "  |  ".join(split_parts[:3])
            bg = LGREY if toggle else WHITE
            pdf.set_fill_color(*bg)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(50, 6, _safe(brand), fill=True)
            pdf.cell(30, 6, str(mentions), fill=True, align="C")
            # colored sentiment badge cell
            pdf.set_fill_color(*dom_c)
            pdf.set_text_color(*WHITE)
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(35, 6, _safe(dom.capitalize()), fill=True, align="C")
            pdf.set_fill_color(*bg)
            pdf.set_text_color(40, 40, 40)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(75, 6, _safe(split_str), fill=True)
            pdf.ln()
            toggle = not toggle
    pdf.ln(4)

    # 4. Top Themes
    pdf.section_title("04  Top Conversation Themes")
    top_themes = summary.get("top_themes", {})
    if top_themes:
        max_t = max(top_themes.values())
        for theme, cnt in list(top_themes.items())[:8]:
            pdf.bar(theme.title(), cnt, max_t, BLUE)
    pdf.ln(4)

    # 5. Consumer Pain Points
    pdf.section_title("05  Consumer Pain Points")
    pain_pts = summary.get("top_pain_points", {})
    if pain_pts:
        max_p = max(pain_pts.values())
        for pain, cnt in list(pain_pts.items())[:6]:
            pdf.bar(pain, cnt, max_p, RED)
    pdf.ln(4)

    # 6. Narratives
    pdf.section_title("06  Dominant Consumer Narratives")
    _INSIGHT_LABELS = [
        ("What is happening?", "trend"),
        ("Why is it happening?", "consumer_driver"),
        ("Why does it matter?", "business_implication"),
        ("What should brands do?", "strategic_action"),
    ]
    for i, narrative in enumerate(insights.get("dominant_narratives", []), 1):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BLUE)
        pdf.cell(0, 6, f"Narrative {i}", ln=True)
        if isinstance(narrative, dict):
            for label, key in _INSIGHT_LABELS:
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(*GREY)
                pdf.set_x(14)
                pdf.cell(0, 5, _safe(label), ln=True)
                pdf.body_text(narrative.get(key, ""), indent=4)
        else:
            pdf.body_text(narrative)
        pdf.ln(3)

    # 7. Recommendations
    pdf.section_title("07  Strategic Recommendations")
    for i, rec in enumerate(insights.get("strategic_recommendations", []), 1):
        if isinstance(rec, dict):
            priority = rec.get("priority", "Medium")
            p_color = RED if priority == "High" else (BLUE if priority == "Medium" else GREY)

            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*NAVY)
            pdf.cell(170, 6, _safe(f"{i}. {rec.get('action', '')}"))
            pdf.set_fill_color(*p_color)
            pdf.set_text_color(*WHITE)
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(20, 6, _safe(priority), fill=True, align="C", ln=True)
            pdf.ln(1)

            for field_label, field_key in [("Why:", "rationale"), ("How:", "how")]:
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(*GREY)
                pdf.set_x(14)
                pdf.cell(12, 5.5, field_label)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(168, 5.5, _safe(rec.get(field_key, "")))
            pdf.ln(3)
        else:
            pdf.body_text(f"{i}. {rec}")
            pdf.ln(2)

    # 8. Source breakdown
    pdf.section_title("08  Data Source Breakdown")
    if "source" in df_processed.columns:
        src_counts = df_processed["source"].value_counts()
        max_src = src_counts.max()
        src_labels = {
            "reddit": "Reddit India",
            "youtube": "YouTube",
            "amazon_review": "Amazon Reviews",
            "google_news": "Google News",
        }
        for src_tag, cnt in src_counts.items():
            label = src_labels.get(src_tag, src_tag)
            pdf.bar(label, cnt, max_src, NAVY)
    pdf.ln(4)

    # Back cover strip
    pdf.set_fill_color(*NAVY)
    pdf.set_y(272)
    pdf.rect(0, pdf.get_y(), 210, 25, "F")
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 6, "India Consumer Pulse AI  |  Strategic intelligence for Indian brands", align="C", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(120, 150, 170)
    pdf.cell(0, 5, "Data reflects Indian digital consumer conversations  |  Not for external distribution", align="C", ln=True)

    return bytes(pdf.output())


# ── Data summary builder ──────────────────────────────────────

def _build_data_summary(df: pd.DataFrame, brands: list[str]) -> dict:
    if df.empty:
        return {}

    sentiment_counts = df["sentiment"].value_counts().to_dict() if "sentiment" in df else {}
    theme_counts = df["theme"].value_counts().to_dict() if "theme" in df else {}
    source_counts = df["source"].value_counts().to_dict()

    # Pain points: filter nulls, count
    pain_points_raw = (
        df["pain_point"].dropna().tolist() if "pain_point" in df else []
    )
    pain_counts = Counter(pain_points_raw)

    # Brand-wise sentiment
    brand_sentiment: dict[str, dict] = {}
    if "brand" in df and "sentiment" in df:
        for brand in df["brand"].unique():
            bdf = df[df["brand"] == brand]
            brand_sentiment[brand] = bdf["sentiment"].value_counts().to_dict()

    # Sample verbatims (up to 8 diverse posts)
    sample_posts: list[str] = []
    if "text" in df:
        for sentiment_val in ["negative", "positive", "mixed", "neutral"]:
            subset = df[df.get("sentiment", pd.Series([])) == sentiment_val] if "sentiment" in df else pd.DataFrame()
            for _, row in subset.head(2).iterrows():
                sample_posts.append(f"[{sentiment_val}] {row['text'][:300]}")
        if not sample_posts:
            sample_posts = df["text"].head(8).apply(lambda t: t[:300]).tolist()

    return {
        "total_records": len(df),
        "sentiment_counts": sentiment_counts,
        "top_themes": dict(list(theme_counts.items())[:8]),
        "top_pain_points": dict(pain_counts.most_common(6)),
        "source_counts": source_counts,
        "brand_sentiment": brand_sentiment,
        "sample_posts": sample_posts[:8],
        "brands_tracked": brands,
    }


# ── AI-powered generators ─────────────────────────────────────

def _generate_executive_summary(summary: dict, category: str, client) -> str:
    prompt = f"""Based on this consumer intelligence data from Indian digital platforms about {category}:

Total conversations analyzed: {summary.get('total_records', 0)}
Sentiment breakdown: {summary.get('sentiment_counts', {})}
Top themes: {list(summary.get('top_themes', {}).keys())[:6]}
Top consumer pain points: {list(summary.get('top_pain_points', {}).keys())[:4]}
Brands mentioned: {list(summary.get('brand_sentiment', {}).keys())}

Sample consumer voices:
{chr(10).join(summary.get('sample_posts', [])[:6])}

Write a 3-paragraph executive intelligence brief for a CMO — not a data summary, a strategic \
interpretation. Follow this structure exactly:

Paragraph 1 — THE NARRATIVE: What is the single dominant consumer story in Indian {category} \
right now? Name the specific consumer segment driving it. Identify the central tension \
(what they want vs. what they are getting). Make it sharp and insight-led.

Paragraph 2 — THE DRIVER: Why is this happening? Go beneath the surface — invoke emotional \
triggers, cultural dynamics, India-specific market mechanics (EMI psychology, service trust gaps, \
aspirational buying, price tier logic, peer validation culture). Cite evidence from the data.

Paragraph 3 — THE IMPLICATION: Where does this narrative lead? What is the strategic risk or \
opportunity for brands in the next 60-90 days? End with one clear direction.

Forbidden phrases: "consumers are increasingly", "there is a growing trend", "data shows that", \
"it is worth noting", "in conclusion". Write as a senior consultant, not a report generator.
Output the three paragraphs only — no headers, no bullet points, no labels."""

    result = client.chat(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        model=settings.OPENROUTER_SUMMARY_MODEL,
        temperature=0.55,
        max_tokens=settings.MAX_TOKENS_SUMMARY,
    )
    return result or _fallback_summary(summary, category)


def _generate_narratives(summary: dict, category: str, client) -> list[dict]:
    all_brands = summary.get("brands_tracked", [])

    # Token budget: base narrative content (3 × 4 fields) needs ~1,500 tokens.
    # Each brand_action entry adds ~100 tokens across 3 narratives (100 × 3 = 300/brand).
    # Calculate how many brands fit in the remaining budget, minimum 1, no cap beyond that.
    _base_reserved = 1_500
    _tokens_per_brand = 300
    max_ai_brands = max(1, (settings.MAX_TOKENS_SUMMARY - _base_reserved) // _tokens_per_brand)
    ai_brands = all_brands[:max_ai_brands]       # get AI-written brand actions
    fallback_brands = all_brands[max_ai_brands:]  # get rule-based brand actions

    brands_str = ", ".join(ai_brands) if ai_brands else "the key brands in this category"

    prompt = f"""Based on consumer intelligence data about Indian {category} consumers:

Themes detected: {list(summary.get('top_themes', {}).keys())[:6]}
Pain points: {list(summary.get('top_pain_points', {}).keys())[:4]}
Sentiment: {summary.get('sentiment_counts', {})}
Brand sentiment: {summary.get('brand_sentiment', {})}

Sample consumer voices:
{chr(10).join(summary.get('sample_posts', [])[:8])}

Generate 3 distinct strategic consumer narratives from this data. Each must be a sharp, \
consulting-style insight — not a summary of what was said, but an interpretation of what it means.

Return a JSON array of 3 objects. Each object must have exactly these 5 fields:

- "trend": WHAT IS HAPPENING — name the specific observable consumer behavior, market shift, or \
  emerging signal. Name the exact consumer segment (e.g. "urban Indian mid-market laptop buyers \
  upgrading from a 5-year-old device"). Think: status signaling, value perception, behavioral \
  change, premiumization, category fatigue. 2-3 sharp sentences.

- "consumer_driver": WHY IT IS HAPPENING — go beneath the surface. Identify the emotional trigger, \
  unmet need, cultural tension, identity aspiration, or India-specific market dynamic driving this \
  behavior (EMI anxiety, service distrust, aspirational buying, price tier logic, peer validation). \
  Avoid restating the trend. 2-3 sentences.

- "business_implication": WHY IT MATTERS — state the strategic risk or opportunity clearly. \
  What is at stake for brands? What category dynamic shifts? What loyalty or conversion signal \
  is building? Make it decision-relevant for a CMO, not descriptive for an analyst. 2-3 sentences.

- "strategic_action": WHAT BRANDS SHOULD DO (generic) — one India-grounded, actionable direction \
  any brand in this category can take. Think: positioning, communication, product, distribution, \
  or community strategy. Specific enough to act on. 2-3 sentences.

- "brand_actions": WHAT EACH BRAND SHOULD DO — a JSON object mapping each brand below to a \
  tailored 2-3 sentence strategic action. Each must be meaningfully different — factor in that \
  brand's specific sentiment, themes, and competitive position in this data. Not just the generic \
  action with the brand name inserted.
  Brands: [{brands_str}]

Return only the JSON array. No markdown, no headers, no extra text outside the array."""

    result = client.chat_json(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        model=settings.OPENROUTER_SUMMARY_MODEL,
        temperature=0.6,
        max_tokens=settings.MAX_TOKENS_SUMMARY,
    )

    if isinstance(result, list) and len(result) >= 1:
        validated = []
        # Fallback actions for brands that didn't fit in the AI prompt
        extra_brand_actions = _make_fallback_brand_actions(fallback_brands, summary)

        for item in result[:3]:
            if isinstance(item, dict):
                ai_brand_actions = item.get("brand_actions", {})
                # Merge AI actions (primary) with fallback actions for remaining brands
                merged_actions = {**extra_brand_actions, **ai_brand_actions}
                validated.append({
                    "trend": item.get("trend", ""),
                    "consumer_driver": item.get("consumer_driver", ""),
                    "business_implication": item.get("business_implication", ""),
                    "strategic_action": item.get("strategic_action", ""),
                    "brand_actions": merged_actions,
                })
        if validated:
            if fallback_brands:
                logger.info(
                    f"Narratives: AI brand actions for {ai_brands}, "
                    f"rule-based for {fallback_brands}"
                )
            return validated
    return _fallback_narratives(summary)


def _generate_recommendations(
    summary: dict, category: str, brands: list[str], client
) -> list[dict]:
    prompt = f"""Based on consumer intelligence data for Indian {category}:

Key themes: {list(summary.get('top_themes', {}).keys())[:5]}
Key pain points: {list(summary.get('top_pain_points', {}).keys())[:4]}
Brand landscape: {list(summary.get('brand_sentiment', {}).keys())}
Sentiment: {summary.get('sentiment_counts', {})}

Generate 4 strategic recommendations for brand managers in the Indian {category} market.

Return a JSON array of 4 objects, each with:
- action: specific action title (5-8 words)
- rationale: why this is needed based on the consumer data (2 sentences)
- how: practical execution direction for the Indian market (2 sentences)
- priority: "High", "Medium", or "Low"

Recommendations must be:
- Specific to India — reference Indian market dynamics (service network, EMI, price tiers, etc.)
- Actionable in 30-90 days by a brand manager
- Grounded in the consumer signals above, not generic best practices"""

    result = client.chat_json(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        model=settings.OPENROUTER_SUMMARY_MODEL,
        temperature=0.4,
        max_tokens=settings.MAX_TOKENS_SUMMARY,
    )
    if isinstance(result, list) and len(result) >= 1:
        validated = []
        for r in result[:4]:
            if isinstance(r, dict):
                validated.append({
                    "action": r.get("action", ""),
                    "rationale": r.get("rationale", ""),
                    "how": r.get("how", ""),
                    "priority": r.get("priority", "Medium"),
                })
        if validated:
            return validated
    return _fallback_recommendations(summary)


# ── Template fallbacks ────────────────────────────────────────

def _fallback_summary(summary: dict, category: str) -> str:
    total = summary.get("total_records", 0)
    top_themes = list(summary.get("top_themes", {}).keys())[:3]
    neg = summary.get("sentiment_counts", {}).get("negative", 0)
    pos = summary.get("sentiment_counts", {}).get("positive", 0)
    dom = "negative" if neg > pos else "positive" if pos > neg else "mixed"
    themes_str = ", ".join(top_themes) if top_themes else "pricing and service quality"

    return (
        f"Analysis of {total} consumer conversations from Indian digital platforms reveals "
        f"a predominantly {dom} sentiment landscape in {category}. "
        f"The most prominent themes driving consumer conversation are: {themes_str}. "
        f"Indian consumers in this category are navigating the tension between premium aspirations "
        f"and practical value expectations — a dynamic unique to the Indian market where "
        f"EMI culture shapes purchase decisions and after-sales service quality disproportionately "
        f"influences brand loyalty. "
        f"Brands that close the gap between their pricing premium and their service quality will "
        f"be best positioned to capture the growing urban Indian consumer tech upgrade cycle."
    )


_STRUCTURED_PAIN_LABELS = [
    "after-sales service quality",
    "value for money",
    "battery life",
    "AI feature relevance",
    "build quality",
    "pricing transparency",
    "software experience",
    "service network coverage",
]


def _make_fallback_brand_actions(brands: list[str], summary: dict) -> dict:
    """Generate simple fallback brand-specific actions based on each brand's sentiment."""
    brand_sentiment = summary.get("brand_sentiment", {})

    # Use only short structured pain labels — never raw AI-generated pain point strings
    pain = list(summary.get("top_pain_points", {}).keys())
    top_pain = next(
        (p for p in pain if len(p) < 40),
        _STRUCTURED_PAIN_LABELS[0],
    )

    actions = {}
    for brand in brands:
        sent = brand_sentiment.get(brand, {})
        dominant = max(sent, key=sent.get) if sent else "neutral"
        if dominant == "negative":
            actions[brand] = (
                f"{brand} should urgently address {top_pain} — its negative sentiment in this "
                f"dataset is disproportionately concentrated here. A proactive public response "
                f"on Reddit India with a concrete service commitment would begin reversing perception."
            )
        elif dominant == "positive":
            actions[brand] = (
                f"{brand} is generating positive signals — amplify this by building India-specific "
                f"content around the themes driving that sentiment. Target r/india and r/suggestalaptop "
                f"where consideration is highest."
            )
        else:
            actions[brand] = (
                f"{brand} should differentiate on {top_pain} by taking a clear public position "
                f"in Indian consumer communities — neutral sentiment means the brand story is not "
                f"cutting through and is at risk of being defined by competitors."
            )
    return actions


def _fallback_narratives(summary: dict) -> list[dict]:
    themes = list(summary.get("top_themes", {}).keys())
    pain_points = list(summary.get("top_pain_points", {}).keys())
    brands = summary.get("brands_tracked", [])
    n2_theme = themes[1] if len(themes) > 1 else "AI features"
    n3_pp = pain_points[0] if pain_points else "pricing opacity"
    top_theme = themes[0] if themes else "consumer tech"
    brand_actions_1 = _make_fallback_brand_actions(brands, summary)
    brand_actions_2 = _make_fallback_brand_actions(brands, summary)
    brand_actions_3 = _make_fallback_brand_actions(brands, summary)

    return [
        {
            "trend": (
                "Urban Indian consumers upgrading their devices are applying a total cost of "
                "ownership lens — weighing after-sales service quality, software longevity, and "
                "resale value alongside the purchase price."
            ),
            "consumer_driver": (
                "India's service infrastructure outside tier-1 cities remains inconsistent, "
                "making post-purchase support a genuine financial risk. "
                "Combined with EMI commitments spanning 12-24 months, a bad service experience "
                "becomes a multi-month financial frustration, not a single incident."
            ),
            "business_implication": (
                "Brands with strong hardware specs but weak service networks are accumulating "
                "a loyalty deficit that will convert to churn at the next upgrade cycle. "
                "This risk is amplified on Reddit India where negative service experiences spread rapidly."
            ),
            "strategic_action": (
                "Publish and promote city-specific service SLAs. "
                "A 5-day maximum turnaround commitment with WhatsApp-based status updates will "
                "directly address the top consumer anxiety in this data."
            ),
            "brand_actions": brand_actions_1,
        },
        {
            "trend": (
                f"Consumer skepticism toward {n2_theme} is building on Indian digital platforms, "
                "with tech-savvy buyers publicly distinguishing between genuine utility and "
                "marketing-driven feature additions."
            ),
            "consumer_driver": (
                "Most AI and premium features in Indian consumer tech are designed for Western "
                "use cases — cloud-dependent, English-first, and disconnected from Indian daily workflows. "
                "Indian consumers recognize this mismatch and are calling it out."
            ),
            "business_implication": (
                "The 'premium features at premium price' justification is losing credibility "
                "in Indian consumer discourse. "
                "Brands maintaining global positioning without India localization risk being "
                "labeled as overpriced in high-engagement communities."
            ),
            "strategic_action": (
                "Identify 2-3 features that demonstrably work offline or in regional language contexts "
                "and build India-specific campaigns around these specific utilities — not the global feature list."
            ),
            "brand_actions": brand_actions_2,
        },
        {
            "trend": (
                f"The {n3_pp} pain point is generating sustained negative conversation in Indian "
                f"{top_theme} communities, with affected consumers actively researching alternatives."
            ),
            "consumer_driver": (
                "Indian consumers share purchase regret and frustration at high rates on Reddit "
                "and Twitter when they feel misled — particularly around pricing transparency, "
                "hidden EMI costs, and after-purchase support gaps."
            ),
            "business_implication": (
                "Each high-engagement negative post on r/india or r/suggestalaptop influences "
                "hundreds of active purchase-intent readers. "
                "The brand damage compounds faster than traditional research cycles can detect."
            ),
            "strategic_action": (
                "Assign a community manager to monitor and respond to high-engagement brand "
                "mentions on key Indian subreddits within 24 hours. "
                "Transparent public responses to complaints outperform deletion in trust recovery."
            ),
            "brand_actions": brand_actions_3,
        },
    ]


def _fallback_recommendations(summary: dict) -> list[dict]:
    pain_points = list(summary.get("top_pain_points", {}).keys())
    themes = list(summary.get("top_themes", {}).keys())

    return [
        {
            "action": "Strengthen India service network response times",
            "rationale": (
                f"After-sales service quality is the single most mentioned pain point in this "
                f"dataset. Indian consumers are sharing negative service experiences at high "
                f"engagement rates — these posts drive disproportionate brand damage."
            ),
            "how": (
                "Commit to a 5-day maximum turnaround SLA for all tier-1 and tier-2 cities. "
                "Proactively communicate repair status via WhatsApp — this channel is expected "
                "by Indian consumers and dramatically reduces escalation rate."
            ),
            "priority": "High",
        },
        {
            "action": "Launch India-specific AI feature campaign",
            "rationale": (
                f"Consumer skepticism around AI laptop features is high in India because "
                f"most features are designed for US/Europe use cases. "
                f"This is creating a 'gimmick' narrative that devalues the premium pricing."
            ),
            "how": (
                "Identify 3 AI features that work without internet and have clear India utility "
                "(regional language support, local business document processing, vernacular voice). "
                "Build campaigns around these specific use cases — not the global feature list."
            ),
            "priority": "High",
        },
        {
            "action": "Introduce transparent no-cost EMI communication",
            "rationale": (
                "EMI culture is central to Indian consumer tech purchasing but consumers feel "
                "misled by hidden fees and conditions. "
                "This is creating pre-purchase distrust that affects conversion at the bottom of the funnel."
            ),
            "how": (
                "Create a dedicated landing page that clearly explains all EMI costs — processing "
                "fees, insurance, penalties — before checkout. "
                "Partner with 2-3 banks for genuinely zero-cost EMI with upfront communication. "
                "This transparency will become a competitive differentiator."
            ),
            "priority": "Medium",
        },
        {
            "action": "Monitor and respond to community feedback on Reddit India",
            "rationale": (
                f"Reddit India (r/india, r/suggestalaptop) is the highest-engagement platform "
                f"for considered consumer tech purchase decisions. "
                f"Brand absence in these communities while competitors engage is a missed opportunity."
            ),
            "how": (
                "Assign a community manager to monitor brand mentions on key Indian subreddits. "
                "Establish a protocol for responding to high-engagement negative posts within 24 hours. "
                "Do not delete or hide negative feedback — address it publicly to rebuild trust."
            ),
            "priority": "Medium",
        },
    ]
