"""
Classifier — India Consumer Pulse AI

Classifies each cleaned record using OpenRouter.
Falls back to keyword-based classification when OpenRouter is unavailable.

Output adds 7 columns to the DataFrame:
  sentiment, theme, sub_theme, pain_point, emotional_driver,
  business_implication, recommended_action
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import pandas as pd

from ai.openrouter_client import get_client
from config.settings import settings

logger = logging.getLogger(__name__)

# AI is called only on the top-N highest-engagement records.
# The rest get instant keyword classification. This keeps the pipeline
# under ~30 seconds regardless of how many records are scraped.
_MAX_AI_RECORDS = 500
_AI_BATCH_SIZE = 10      # 10 records × ~100 tokens/record ≈ 1,000 tokens output, well under 2,000
_AI_WORKERS = 4          # parallel API calls

CLASSIFICATION_COLUMNS = [
    "sentiment", "theme", "sub_theme", "pain_point",
    "emotional_driver", "business_implication", "recommended_action",
]

_DEFAULT_CLASSIFICATION = {
    "sentiment": "neutral",
    "theme": "general discussion",
    "sub_theme": "general",
    "pain_point": None,
    "emotional_driver": "curiosity",
    "business_implication": "Consumer conversation detected — further analysis needed.",
    "recommended_action": "Monitor this theme for emerging patterns.",
}

_SYSTEM_PROMPT = """You are a senior consumer intelligence analyst specializing in the Indian market.
You have 18 years of experience decoding Indian consumer behavior in the Consumer Tech category.
You understand Hinglish discourse, Indian price sensitivity, aspirational buying patterns, and
the cultural dynamics of Indian digital communities."""

_CLASSIFY_PROMPT_TEMPLATE = """Analyze these {n} consumer posts from Indian digital platforms about {category}.

For EACH post, return a JSON object with exactly these fields:
- sentiment: one of "positive", "negative", "neutral", "mixed"
- theme: 2-4 word primary topic (e.g., "battery life", "value for money", "after-sales service", "AI features", "build quality", "camera quality", "pricing", "software experience")
- sub_theme: more specific aspect in 2-4 words
- pain_point: specific consumer frustration expressed as a phrase, or null if none
- emotional_driver: one word — aspiration, frustration, satisfaction, disappointment, excitement, skepticism, pride, or anxiety
- business_implication: one sentence on what this means for brands selling in India (be specific, not generic)
- recommended_action: one concrete action a brand manager can take (specific, not vague)

Return ONLY a valid JSON array with exactly {n} objects in the same order as the posts.
Do not add explanations. Do not fabricate brand names not present in the text.

Posts:
{posts}"""


# ── Public API ────────────────────────────────────────────────

def classify_dataframe(
    df: pd.DataFrame, category: str, brands: list[str]
) -> pd.DataFrame:
    if df.empty:
        for col in CLASSIFICATION_COLUMNS:
            df[col] = None
        return df

    client = get_client()
    total = len(df)

    # Split: top-N by engagement get AI classification; the rest get keyword classification.
    # This caps AI API calls at a fixed ceiling regardless of scrape volume.
    if total > _MAX_AI_RECORDS:
        logger.info(
            f"Classifying {total} records: AI on top {_MAX_AI_RECORDS} by engagement, "
            f"keyword on remaining {total - _MAX_AI_RECORDS}"
        )
        df_sorted = df.copy().sort_values("engagement", ascending=False)
        ai_positions  = list(range(_MAX_AI_RECORDS))
        kw_positions  = list(range(_MAX_AI_RECORDS, total))
        df_ai = df_sorted.iloc[ai_positions].copy()
        df_kw = df_sorted.iloc[kw_positions].copy()
    else:
        logger.info(f"Classifying all {total} records with AI")
        df_ai = df.copy()
        df_kw = pd.DataFrame(columns=df.columns)

    # ── Keyword classify the bulk (instant) ──────────────────
    if not df_kw.empty:
        kw_results = [_keyword_classify(t) for t in df_kw["text"].tolist()]
        for col in CLASSIFICATION_COLUMNS:
            df_kw[col] = [r.get(col) for r in kw_results]

    # ── AI classify the top records in parallel batches ───────
    texts = df_ai["text"].tolist()
    batches = [texts[i: i + _AI_BATCH_SIZE] for i in range(0, len(texts), _AI_BATCH_SIZE)]
    ai_results: list[Optional[list[dict]]] = [None] * len(batches)

    def _run_batch(idx_batch: tuple[int, list[str]]) -> tuple[int, list[dict]]:
        idx, batch = idx_batch
        if client.is_available:
            result = _classify_batch_ai(batch, category, client)
        else:
            result = None
        if result is None or len(result) != len(batch):
            logger.warning(f"AI failed batch {idx + 1} — using keyword fallback")
            result = [_keyword_classify(t) for t in batch]
        return idx, result

    logger.info(
        f"AI classifying {len(texts)} records in {len(batches)} batches "
        f"({_AI_BATCH_SIZE}/batch, {_AI_WORKERS} parallel workers)"
    )
    with ThreadPoolExecutor(max_workers=_AI_WORKERS) as pool:
        futures = {pool.submit(_run_batch, (i, b)): i for i, b in enumerate(batches)}
        for future in as_completed(futures):
            idx, result = future.result()
            ai_results[idx] = result

    # Flatten in order
    flat_ai: list[dict] = []
    for result in ai_results:
        flat_ai.extend(result or [])

    for col in CLASSIFICATION_COLUMNS:
        df_ai[col] = [r.get(col) for r in flat_ai]

    # Re-combine in original engagement order (AI records first, then kw records)
    combined = pd.concat([df_ai, df_kw], ignore_index=True)
    logger.info(f"Classification complete: {len(combined)} records total")
    return combined


# ── AI classification ─────────────────────────────────────────

def _classify_batch_ai(
    texts: list[str], category: str, client
) -> Optional[list[dict]]:
    numbered = "\n\n".join(f"{i + 1}. {t[:600]}" for i, t in enumerate(texts))
    prompt = _CLASSIFY_PROMPT_TEMPLATE.format(
        n=len(texts), category=category, posts=numbered
    )

    result = client.chat_json(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        model=settings.OPENROUTER_CLASSIFICATION_MODEL,
        temperature=0.15,
        max_tokens=settings.MAX_TOKENS_CLASSIFY,
    )

    if not isinstance(result, list):
        return None

    # Validate and fill missing fields
    validated = []
    for item in result:
        if not isinstance(item, dict):
            validated.append(_DEFAULT_CLASSIFICATION.copy())
            continue
        validated.append({
            "sentiment": _safe_str(item.get("sentiment"), "neutral",
                                   {"positive", "negative", "neutral", "mixed"}),
            "theme": _safe_str(item.get("theme"), "general discussion"),
            "sub_theme": _safe_str(item.get("sub_theme"), "general"),
            "pain_point": item.get("pain_point"),
            "emotional_driver": _safe_str(
                item.get("emotional_driver"), "curiosity",
                {"aspiration", "frustration", "satisfaction", "disappointment",
                 "excitement", "skepticism", "pride", "anxiety", "curiosity"},
            ),
            "business_implication": _safe_str(
                item.get("business_implication"),
                "Monitor this consumer signal for brand strategy implications.",
            ),
            "recommended_action": _safe_str(
                item.get("recommended_action"),
                "Track this theme over coming weeks for trend confirmation.",
            ),
        })

    return validated


# ── Keyword fallback classifier ───────────────────────────────

_POS_WORDS = {
    "great", "good", "excellent", "love", "amazing", "worth", "best", "recommend",
    "happy", "satisfied", "impressed", "awesome", "brilliant", "fantastic",
    "perfect", "outstanding", "superb", "incredible", "stunning",
}
_NEG_WORDS = {
    "bad", "worst", "terrible", "disappointed", "overpriced", "avoid", "issues",
    "problem", "broken", "regret", "waste", "awful", "poor", "horrible",
    "useless", "pathetic", "disgusting", "nightmare", "disaster", "failure",
    "letdown", "ridiculous", "unacceptable",
}
_THEME_MAP = {
    "battery life": ["battery", "charge", "charging", "mah", "backup"],
    "value for money": ["worth", "price", "expensive", "cheap", "budget", "value", "cost"],
    "after-sales service": ["service", "support", "warranty", "repair", "center", "technician"],
    "AI features": ["ai", "copilot", "neural", "artificial intelligence", "npu", "on-device"],
    "build quality": ["build", "design", "premium", "plastic", "metal", "hinge", "keyboard"],
    "camera quality": ["camera", "photo", "video", "lens", "megapixel", "photography"],
    "performance": ["performance", "speed", "fast", "slow", "lag", "processor", "chip", "throttle"],
    "display quality": ["display", "screen", "oled", "amoled", "resolution", "bright"],
    "pricing": ["price", "expensive", "overpriced", "emi", "cost", "tax", "rupee"],
    "software experience": ["software", "ui", "update", "os", "android", "windows", "bloatware"],
}
_PAIN_MAP = {
    "High price relative to features": ["expensive", "overpriced", "india tax"],
    "Poor after-sales service quality": ["service center", "warranty issue", "support"],
    "Battery life below expectations": ["battery drain", "poor battery", "battery backup"],
    "Thermal throttling in Indian summers": ["overheating", "throttle", "hot"],
    "AI features not useful in India": ["copilot", "region locked", "ai feature", "gimmick"],
    "Build quality and durability issues": ["broken", "cracked", "hinge", "keyboard fail"],
    "Data loss from service centers": ["data loss", "factory reset", "lost data"],
}


def _keyword_classify(text: str) -> dict:
    tl = text.lower()
    pos = sum(1 for w in _POS_WORDS if w in tl)
    neg = sum(1 for w in _NEG_WORDS if w in tl)

    if pos > neg:
        sentiment = "positive"
        emotion = "satisfaction"
    elif neg > pos:
        sentiment = "negative"
        emotion = "frustration"
    elif pos == neg > 0:
        sentiment = "mixed"
        emotion = "skepticism"
    else:
        sentiment = "neutral"
        emotion = "curiosity"

    theme = "general discussion"
    max_hits = 0
    for t, kws in _THEME_MAP.items():
        hits = sum(1 for k in kws if k in tl)
        if hits > max_hits:
            max_hits = hits
            theme = t

    pain_point = None
    if sentiment in ("negative", "mixed"):
        for pp, kws in _PAIN_MAP.items():
            if any(k in tl for k in kws):
                pain_point = pp
                break

    return {
        "sentiment": sentiment,
        "theme": theme,
        "sub_theme": theme,
        "pain_point": pain_point,
        "emotional_driver": emotion,
        "business_implication": (
            f"Consumer {sentiment} sentiment around '{theme}' signals a brand attention area "
            f"in the Indian {_guess_segment(tl)} segment."
        ),
        "recommended_action": (
            "Monitor volume and intensity of this theme over the next 2 weeks before escalating."
        ),
    }


def _guess_segment(text: str) -> str:
    if any(w in text for w in ["laptop", "macbook", "thinkpad", "spectre", "zenbook"]):
        return "laptop"
    if any(w in text for w in ["phone", "iphone", "samsung", "oneplus", "smartphone"]):
        return "smartphone"
    return "consumer tech"


def _safe_str(value, default: str, allowed: Optional[set] = None) -> str:
    if not isinstance(value, str) or not value.strip():
        return default
    if allowed and value.lower() not in allowed:
        return default
    return value.strip()
