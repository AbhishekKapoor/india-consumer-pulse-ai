# CLAUDE.md — India Consumer Pulse AI

> Single source of truth for engineering decisions, product philosophy, AI architecture, and coding standards. Every contributor must read this before writing code.

---

## 1. Product Vision

India Consumer Pulse AI is an AI-powered consumer intelligence platform purpose-built for the Indian market. It transforms raw social signal into structured strategic insight — **narrative intelligence**: what Indian consumers are feeling, why, how that feeling is shifting, and what brands should do.

**Core thesis:** Indian consumer behavior is underrepresented in global intelligence tools. The cultural context, language mix (Hinglish), platform behavior, and purchase logic of Indian consumers require a dedicated intelligence layer — not a generic global tool with an India filter.

**Ultimate ambition:** Become the Bloomberg Terminal of Indian consumer intelligence.

**Categories (phased):** Phase 1: Consumer Tech → Phase 2: EV, FMCG, Wellness → Phase 3: Retail, Finance, QSR → Phase 4: Beauty

**Platform outputs are always:** Actionable, interpretive, strategically framed, designed for decision-makers.

---

## 2. MVP Goals

Scoped to Consumer Tech in India. Must deliver:

1. **Trend Detection** — Emerging topics gaining momentum before mainstream news
2. **Narrative Analysis** — Emotional and rational story behind a trend
3. **Brand Intelligence** — How brands are perceived, compared, and discussed
4. **Consumer Pain Points** — Friction with products, pricing, service, category expectations
5. **Strategic Recommendations** — Brand strategy a CMO can act on
6. **Weekly Pulse Report** — Structured Streamlit dashboard report

**Success criteria:**
- 5+ Consumer Tech sub-categories (smartphones, wearables, laptops, audio, smart home)
- 3+ data sources (Reddit India, Twitter/X, app store reviews)
- AI-written narrative weekly reports
- Demo-able to enterprise client within 60 days
- Under $50/month in API and infrastructure costs

---

## 3. Primary Users

**Tier 1 (MVP):**
- Brand Managers at Consumer Tech companies — weekly consumer pulse, trend alerts, brand perception
- Product Managers at D2C brands — feature wants, complaints, category evolution for roadmap
- Startup Founders — market intelligence without a research budget

**Tier 2 (Phase 2):** VC Analysts, Strategy Consultants, CMOs at mid-market Indian brands

---

## 4. Product Principles

- **P1: Insight over data** — Never show raw data. Always interpret.
- **P2: Narrative first** — Every output tells a coherent story.
- **P3: India-native** — Every decision reflects Indian market context.
- **P4: Minimum viable, maximum strategic** — Lean build, rich strategic value.
- **P5: Modular by design** — Every component is replaceable without breaking others.
- **P6: Founder-scale economics** — Every architectural choice defensible at $0 MRR.
- **P7: Actionability as exit criterion** — Observation + interpretation + recommendation = complete insight.
- **P8: Transparency of source** — Every insight traceable to source data. No hallucinated trends.
- **P9: Indian linguistic complexity** — Handle Hinglish, regional transliterations, code-switching, sarcasm.
- **P10: Design for the non-analyst** — Consumable in under 5 minutes without training.

---

## 5. Technical Architecture

### Pipeline

```
[Data Sources] → [Ingestion (Apify + Python)] → [Raw Store (CSV)]
→ [AI Processing (OpenRouter)] → [Insight Store (CSV/JSON)]
→ [Insight Generation] → [Dashboard (Streamlit)] → [Delivery]
```

### Stack

| Layer | MVP Tool | Scale Tool |
|---|---|---|
| Scraping | Apify Ultimate Scraper | Custom scrapers + Airflow |
| Raw storage | CSV → Google Sheets | PostgreSQL / BigQuery |
| AI processing | OpenRouter API | Claude API + fine-tuned models |
| Insight storage | CSV + JSON | Supabase / PostgreSQL |
| Orchestration | Manual → n8n (post-MVP) | Prefect / Dagster |
| Frontend | Streamlit | React + Next.js |
| Deployment | Streamlit Cloud | AWS / GCP |

### Core Services

1. **Data Ingestion** (`/ingestion/`) — Pulls raw posts, comments, reviews. Outputs structured JSON rows.
2. **Preprocessing** (`/processing/`) — Cleans, detects language, normalizes Hinglish, deduplicates, tags.
3. **AI Analysis** (`/ai/`) — Sends batches to OpenRouter via `openrouter_client.py`. Extracts sentiment, topics, pain points, brand mentions, trend signals.
4. **Insight Aggregation** (`/insights/`) — Aggregates AI outputs, identifies dominant narratives, calculates trend velocity.
5. **Report Generation** (`/reports/`) — Compiles insights into structured report format. Outputs to Streamlit and optionally PDF.
6. **Dashboard** (`/dashboard/`) — Streamlit app rendering weekly pulse, trends, brand intelligence, recommendations.

---

## 6. Folder Structure

```
india-consumer-pulse-ai/
├── CLAUDE.md
├── README.md
├── .env                             # Never commit
├── .env.example
├── requirements.txt
├── .gitignore
│
├── config/
│   ├── categories.yaml
│   ├── sources.yaml
│   ├── prompts/                     # All AI prompt templates (versioned .txt files)
│   │   ├── sentiment_analysis.txt
│   │   ├── trend_detection.txt
│   │   ├── narrative_synthesis.txt
│   │   ├── brand_intelligence.txt
│   │   └── strategic_recommendation.txt
│   └── settings.yaml
│
├── ingestion/
│   ├── reddit_ingester.py
│   ├── twitter_ingester.py
│   ├── appstore_ingester.py
│   ├── youtube_ingester.py
│   ├── news_ingester.py
│   └── base_ingester.py
│
├── processing/
│   ├── cleaner.py
│   ├── language_detector.py
│   ├── deduplicator.py
│   ├── tagger.py
│   └── validator.py
│
├── ai/
│   ├── openrouter_client.py         # ALL AI calls go through here — no exceptions
│   ├── sentiment_analyzer.py
│   ├── topic_clusterer.py
│   ├── brand_extractor.py
│   ├── pain_point_extractor.py
│   ├── trend_detector.py
│   └── batch_processor.py
│
├── insights/
│   ├── aggregator.py
│   ├── narrative_builder.py
│   ├── trend_ranker.py
│   ├── brand_intelligence.py
│   └── recommendation_engine.py
│
├── reports/
│   ├── weekly_pulse.py
│   ├── pdf_exporter.py
│   ├── sheets_exporter.py
│   └── templates/
│       ├── executive_summary.txt
│       ├── trend_section.txt
│       └── brand_section.txt
│
├── dashboard/
│   ├── app.py
│   ├── pages/
│   │   ├── 01_weekly_pulse.py
│   │   ├── 02_trend_explorer.py
│   │   ├── 03_brand_intelligence.py
│   │   ├── 04_consumer_pain_points.py
│   │   └── 05_strategic_recommendations.py
│   ├── components/
│   │   ├── insight_card.py
│   │   ├── trend_chart.py
│   │   ├── brand_heatmap.py
│   │   └── narrative_panel.py
│   └── styles/theme.css
│
├── data/
│   ├── raw/                         # gitignored
│   ├── processed/                   # gitignored
│   ├── insights/                    # gitignored
│   └── reports/                     # gitignored
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_processing.py
│   ├── test_ai.py
│   ├── test_insights.py
│   └── fixtures/
│
├── scripts/
│   ├── run_daily_pipeline.py
│   ├── run_weekly_report.py
│   ├── backfill_data.py
│   └── validate_outputs.py
│
├── n8n/workflows/
└── logs/
```

**Rules:**
- Never put business logic in `dashboard/`. The dashboard renders only.
- Never import from `dashboard/` in any other module.
- All configuration in `config/`. No hardcoded values in business logic.
- All prompts in `config/prompts/`. Never embed prompt strings in Python files.
- `data/` contents are always gitignored.

---

## 7. Coding Standards

- Python 3.11+, `venv`, `python-dotenv`, all dependencies pinned in `requirements.txt`
- PEP 8 strictly; max 100 chars/line; `black` for formatting; `ruff` for linting
- Type hints on all function signatures
- Dataclasses or Pydantic models for structured data — never raw dicts between modules
- One function, one responsibility; split functions over 30 lines

### Error Handling

```python
def fetch_reddit_posts(subreddit: str, limit: int) -> Optional[list[dict]]:
    try:
        posts = reddit_client.get_posts(subreddit, limit)
        return posts
    except RateLimitError as e:
        logger.warning(f"Reddit rate limit hit for r/{subreddit}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching r/{subreddit}: {e}")
        raise
```

### Configuration Pattern

```python
from config.loader import settings
model = settings.ai.openrouter_model  # Never os.environ directly in business logic
```

### Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Files | snake_case | `trend_detector.py` |
| Classes | PascalCase | `TrendDetector` |
| Functions | snake_case | `detect_emerging_trends()` |
| Constants | UPPER_SNAKE | `MAX_TOKENS_PER_BATCH` |
| Config keys | snake_case | `openrouter_model` |
| Streamlit pages | `NN_page_name.py` | `01_weekly_pulse.py` |

### Import Order

```python
# 1. Standard library
import os, json
from datetime import datetime
from typing import Optional, List

# 2. Third-party
import streamlit as st
import pandas as pd

# 3. Internal
from config.loader import settings
from ai.openrouter_client import OpenRouterClient
```

### Testing

- Every ingester: fixture-based test (no live API calls)
- Every AI function: mocked response test
- `pytest` with `pytest-mock`; happy path + one failure path per function
- Run `pytest tests/` before every commit

---

## 8. Streamlit UI Guidelines

- `st.set_page_config(layout="wide")` always
- Sidebar: navigation and filters only — no content
- Maximum 3 levels of information hierarchy per page
- Cache all data loads: `@st.cache_data(ttl=3600)`
- Cache heavy computation: `@st.cache_resource`
- **Never run AI API calls in the Streamlit render loop** — pre-generate all insights in the pipeline
- Charts: use Plotly (not Matplotlib); every chart needs a plain-English strategic caption
- Tables: `st.dataframe()` with column configs; never render raw DataFrames
- Narratives: `st.markdown()` with bold key claim in every paragraph

### Color Standards

- Primary: `#1a1a2e` | Accent: `#e94560` | Positive: `#00b894` | Neutral: `#636e72`
- Red = concern/decline, Green = opportunity/growth, Blue = neutral data

### Five Dashboard Pages (MVP)

1. **Weekly Pulse** — Top 3 narrative headlines, category momentum, week-over-week volume, featured consumer quote
2. **Trend Explorer** — Ranked trends with momentum arrows, volume over time, trajectory prediction
3. **Brand Intelligence** — Perception matrix, brand comparison, association themes, narrative shifts
4. **Consumer Pain Points** — Ranked pain points, evolution over time, unmet needs, verbatim evidence
5. **Strategic Recommendations** — 3-5 prioritized actions (context → insight → action → outcome + confidence score)

### Anti-Patterns

Never build: pie charts of sentiment split, raw data tables as primary content, recommendations without supporting evidence, charts without strategic captions, metrics without time context, more than 5 key metrics per page.

---

## 9. AI Prompt Engineering Standards

All prompts live in `config/prompts/` as versioned `.txt` files with `{variable}` placeholders. Never hardcode prompts in Python.

### Standard Prompt Template

```
ROLE:
You are a senior consumer intelligence analyst specializing in Indian digital markets.
Deep knowledge of Indian consumer behavior, Hinglish discourse, and the {category} category in India.

CONTEXT:
Data from Indian digital platforms (Reddit, Twitter/X, app reviews)
collected between {start_date} and {end_date}.
Category: {category} | Subcategory: {subcategory}

DATA:
{raw_data}

TASK:
{specific_task_instruction}

OUTPUT FORMAT:
{structured_output_schema}

CONSTRAINTS:
- Base every claim on the data provided. Do not infer trends not present in the data.
- Plain English for brand managers, not data scientists.
- If data is insufficient for a conclusion, say so explicitly.
- Cite approximate source volume (e.g., "seen in ~40% of posts analyzed").
- Never fabricate brand names, product names, or statistics.
```

### Output Schema (JSON for pipeline)

```json
{
  "dominant_narrative": "string",
  "trend_signals": [
    {"trend": "string", "momentum": "rising|stable|declining",
     "volume_indicator": "string", "consumer_quote_example": "string"}
  ],
  "brand_mentions": [
    {"brand": "string", "sentiment": "positive|negative|mixed|neutral", "key_theme": "string"}
  ],
  "pain_points": ["string"],
  "strategic_recommendation": "string",
  "confidence": "high|medium|low",
  "confidence_rationale": "string"
}
```

### Prompt Engineering Rules

1. Always specify the audience
2. Always specify the Indian context — never implicit
3. Always constrain hallucination — explicitly forbid fabrication in every prompt
4. Always define output format (JSON for pipeline, prose for reports)
5. Temperature 0.3 for analytical tasks; 0.7 for narrative/creative synthesis
6. Batch 10-20 posts per API call — never one post per call
7. Include negative space — tell the model what NOT to do
8. Validate all outputs against schema before storing; reject malformed responses

### Prompt Versioning

- Every prompt file is versioned: `trend_detection_v2.txt`
- Old versions archived, not deleted
- Prompt changes logged in `config/prompts/CHANGELOG.md`
- Test against at least 5 real data samples before deploying

### Token Budgets

```python
TOKEN_BUDGETS = {
    "sentiment_analysis": 256,
    "topic_extraction": 512,
    "brand_extraction": 512,
    "trend_detection": 1024,
    "narrative_synthesis": 2048,
    "strategic_recommendation": 2048,
    "weekly_report_section": 4096,
}
```

---

## 10. Data Pipeline Standards

**Pipeline must be:** idempotent (running twice = same result), resumable (failure at stage 3 ≠ restart from stage 1), auditable (every run logged with counts and timestamps).

### Stages

```
Stage 1: Ingestion     → raw JSON → data/raw/{source}/{YYYY-MM-DD}/
Stage 2: Preprocessing → clean, dedup, tag → data/processed/{YYYY-MM-DD}/
Stage 3: AI Analysis   → batches to OpenRouter → data/insights/{YYYY-MM-DD}/
Stage 4: Aggregation   → narratives, trend rankings, brand scores → data/reports/
Stage 5: Report Gen    → narrative sections → Streamlit / PDF export
```

### Data Schemas

```python
@dataclass
class RawRecord:
    id: str                    # source:platform_id
    source_platform: str       # reddit|twitter|playstore|youtube|news
    source_url: str
    content: str
    author: str                # anonymized at ingestion
    timestamp: datetime
    category: str
    subcategory: str
    metadata: dict
    ingested_at: datetime
    pipeline_run_id: str

@dataclass
class InsightRecord:
    id: str
    source_record_id: str
    category: str
    subcategory: str
    sentiment: str
    dominant_theme: str
    brand_mentions: list[str]
    pain_points: list[str]
    trend_signals: list[dict]
    ai_model_used: str
    prompt_version: str
    processed_at: datetime
    confidence: str
    raw_ai_response: str       # store full response for audit
```

### Data Quality Rules

- Minimum 20 chars per post; filter emoji-only and one-word posts
- Maximum 7 days old for weekly pipeline
- Deduplication: SHA-256 hash of normalized content
- Spam filter: < 5 karma (Reddit) or < 10 followers (Twitter)
- Accept English and Hinglish; flag but don't reject regional language posts
- Minimum 5 records per AI analysis batch

### Scheduling

```
Daily:   00:30 IST — ingestion + preprocessing + AI analysis
Weekly:  07:00 IST Monday — aggregation + report generation
Alerts:  Every 4 hours — spike check (>2x average volume)
```

---

## 11. Category Taxonomy

```yaml
categories:
  consumer_tech:
    display_name: "Consumer Tech"
    subcategories:
      smartphones:
        brands: [Apple, Samsung, OnePlus, Xiaomi, Realme, Vivo, OPPO, iQOO, Motorola, Nothing]
        keywords: [phone, smartphone, mobile, iphone, android, flagship, midrange, budget phone]
        subreddits: [r/india, r/indiangaming, r/oneplus, r/samsung, r/xiaomi]
      wearables:
        brands: [boAt, Noise, Fire-Boltt, Amazfit, Apple, Samsung, OnePlus, Titan]
        keywords: [smartwatch, earbuds, tws, earphones, fitness band, wearable]
        subreddits: [r/india, r/wearables]
      laptops:
        brands: [Dell, HP, Lenovo, ASUS, Acer, Apple, MSI, Samsung]
        keywords: [laptop, macbook, notebook, ultrabook, gaming laptop, work from home]
        subreddits: [r/india, r/laptops, r/suggestalaptop]
      audio:
        brands: [Sony, JBL, Bose, Sennheiser, boAt, Noise, Skullcandy, Marshall]
        keywords: [headphones, speaker, bluetooth speaker, anc, noise cancelling, audio]
        subreddits: [r/india, r/headphones, r/audiophile]
      smart_home:
        brands: [Amazon Echo, Google Nest, Xiaomi, Realme, TP-Link, Havells, Orient]
        keywords: [smart tv, smart bulb, alexa, google home, iot, smart plug, automation]
        subreddits: [r/india, r/smarthome]
```

**Taxonomy Rules:**
- Every record tagged with `category` + `subcategory` at ingestion
- Keyword matching is case-insensitive; handles Hinglish variants
- Brand names normalized to canonical form at preprocessing (e.g., "mi" → "Xiaomi")
- A record can match multiple subcategories — store all, use primary for routing
- Update taxonomy YAML to add brands; never hardcode brand lists in Python

---

## 12. AI Insight Quality Standards

### The Four Tests (all must pass)

1. **Grounded** — Based on actual data. Can point to a source cluster.
2. **Specific** — Specific to India and this category, not generic.
3. **Novel** — Tells the user something they likely didn't know.
4. **Actionable** — Leads to a decision a brand manager can take.

### Confidence Levels

```
HIGH:   >50 data points, consistent signal, clear narrative
MEDIUM: 15-50 data points, moderate consistency
LOW:    <15 data points, emerging signal
```

Always display confidence with every insight. Never hide uncertainty.

### Insight Output Structure

Every complete insight must answer all four questions:

| Question               | Output               |
| ---------------------- | -------------------- |
| What is happening?     | Trend                |
| Why is it happening?   | Consumer driver      |
| Why does it matter?    | Business implication |
| What should brands do? | Strategic action     |

An insight missing any of the four is incomplete and must not be surfaced to the dashboard.

### Narrative Construction

1. Identify the dominant emotion (frustration, excitement, confusion, aspiration)
2. Find the central tension (what consumers want vs. what they're getting)
3. Locate the inflection point (new, evolving, or entrenched narrative)
4. Contextualize for India (price sensitivity, aspirational buying, trust dynamics, EMI culture)
5. Derive the implication (opportunity or threat if narrative continues)

### Hallucination Prevention

- Tag all AI insights with source record count
- Minimum 10 source records before generating a subcategory insight
- Validate all brand mentions against actual brand mentions in source data
- Schema-validate every AI JSON response before storage; reject malformed outputs
- All insights require `confidence` field before surfacing to dashboard
- Spot-check 5% of insights weekly for human review

### Insight Refresh Cadence

- Trend signals, brand intelligence: refreshed daily
- Pain points, strategic recommendations, executive narratives: refreshed weekly (Monday)

---

## 13. Indian Market Context

These rules must inform every prompt, insight, and recommendation.

**Price Architecture:** <₹10K (mass), ₹10K-25K (mid), ₹25K-50K (premium), >₹50K (ultra-premium). Tag sentiment with price tier context.

**Aspirational vs. Practical:** Distinguish desire-language from purchase-intent-language in data.

**Trust Hierarchy:** Peer recommendations > influencer reviews > brand claims > advertising. Weight peer-generated content higher in insight generation.

**Festival Buying:** Sentiment and purchase intent spike at Diwali, Holi, Republic Day, Independence Day sales. Flag sale-period sentiment separately.

**EMI Culture:** Treat EMI-related sentiment as a distinct signal layer, not generic price sentiment.

**Platform Weighting:**

| Platform | Weight | Why |
|---|---|---|
| Reddit India | High | Urban, tech-savvy, high-intent discussions |
| Play Store reviews | High | High-intent, post-purchase, specific |
| Twitter/X | Medium | Real-time but noisy; good for brand crisis signals |
| YouTube comments | Medium | Mix of aspirational and experienced users |
| Quora | Medium | Considered, long-form purchase intent |
| News comments | Low | Often politically influenced |

**Narrative vs. Data Insight:** Always aim for narrative insight ("Indian consumers have accepted X — frustration has shifted to Y"). Data insight ("23% of posts mention battery life") is a supporting layer only.

---

## 14. Security & Privacy

- **No PII storage** — Anonymize author identifiers with one-way hashing at ingestion
- **Raw content purged after 30 days** — Processed insights kept 12 months
- **No scraping that violates ToS** — Official APIs and Apify only; document legal basis per source
- All API keys in `.env` — never in code or config YAML
- `.env` always in `.gitignore` — verify before every commit
- Use separate API keys for dev and production; rotate every 90 days
- Never log API keys, even partially
- Schema-validate all AI outputs before storage; reject malformed responses
- Filter profanity/harmful content before dashboard display

---

## 15. Cost Optimization

**Target: under $50/month**

| Service | Expected Cost |
|---|---|
| OpenRouter API | ~$15-25/month |
| Reddit API | $0 |
| Twitter API v2 | $0-100/month |
| Streamlit Cloud | $0 |
| n8n (self-hosted) | $0-5/month |

**Optimization patterns:**
- Batch 10-20 posts per API call (10-15x cost reduction vs. one post per call)
- Cache AI results for near-identical content (cosine similarity > 0.95)
- Use cheaper models for classification; stronger models only for narrative generation
- Run heavy AI processing 01:00-04:00 IST (off-peak)
- Skip AI for posts < 20 chars, pure links, or spam-flagged content

```python
TOKEN_BUDGETS = {  # See Section 9 for full table
    "sentiment_analysis": 256,
    "weekly_report_section": 4096,
}
```

---

## 16. Deployment Standards

### Environment Variables

```bash
# .env.example
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/auto
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=IndiaConsumerPulseAI/1.0
TWITTER_BEARER_TOKEN=
GOOGLE_SHEETS_CREDENTIALS_JSON=
GOOGLE_SHEETS_SPREADSHEET_ID=
APP_ENV=development
LOG_LEVEL=INFO
PIPELINE_BATCH_SIZE=15
MAX_TOKENS_DEFAULT=1024
```

### Deployment Checklist

- [ ] `pytest tests/` passes
- [ ] No API keys in code (`grep -r "sk-" .` returns empty)
- [ ] `.env` in `.gitignore`
- [ ] `requirements.txt` updated
- [ ] New prompts versioned and tested against 5 real samples
- [ ] Dashboard renders without errors locally
- [ ] Pipeline dry-run completed (`--dry-run` flag, no data written)

### Versioning

Semantic versioning: `MAJOR.MINOR.PATCH`
- PATCH: Bug fixes, prompt tweaks, UI copy
- MINOR: New subcategory, data source, or dashboard section
- MAJOR: New category, architectural change, breaking API changes

---

## 17. Git Standards

### Commit Format

```
<type>(<scope>): <short description>
[optional body — explain WHY, not WHAT]
```

**Types:** `feat`, `fix`, `data`, `prompt`, `pipeline`, `ui`, `config`, `docs`, `refactor`, `test`, `chore`

**Scopes:** `ingestion`, `processing`, `ai`, `insights`, `reports`, `dashboard`, `config`, `pipeline`

**Examples:**
```
feat(ingestion): add Play Store review ingester for smartphone category
prompt(ai): update trend_detection prompt to v3 with Hinglish improvements
fix(processing): resolve deduplication bug for Reddit cross-posts
data(config): add audio subcategory brands to taxonomy
```

**Branch strategy:**
```
main       — stable, deployable, tagged releases only
dev        — integration branch, must pass all tests
feat/<name>   — feature development
fix/<name>    — bug fixes
prompt/<name> — prompt development and testing
```

**Pre-commit:** `black .` → `ruff check .` → `pytest tests/` → confirm no secrets staged

---

## 18. Logging Standards

```python
logger.debug(f"Processing batch {batch_id} with {len(records)} records")  # dev only
logger.info(f"Ingestion complete: {count} posts from r/{subreddit}")
logger.warning(f"Rate limited by Reddit API, waiting 60s")
logger.error(f"AI analysis failed for batch {batch_id}: {e}")
logger.critical(f"Google Sheets write failed — data may be lost: {e}")
```

**Pipeline run log** (Google Sheets columns): `run_id`, `stage`, `started_at`, `completed_at`, `input_count`, `output_count`, `error_count`, `tokens_used`, `cost_usd`, `status`, `notes`

**MVP monitoring:** Check pipeline log daily. Investigate before next run if `status=failed` or `error_count > 10`.

---

## 19. API Integration Standards

```python
class BaseAPIClient:
    def __init__(self, api_key: str, rate_limit_per_minute: int):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(rate_limit_per_minute)
        self.session = requests.Session()

    def _make_request(self, method: str, url: str, **kwargs) -> dict:
        self.rate_limiter.wait_if_needed()
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise
        except requests.Timeout:
            logger.warning(f"Timeout on request to {url}")
            raise
```

**Retry policy:** 3 attempts, 2x backoff (1s, 2s, 4s), retry on 429/500/502/503/504.

**Rate limits:** Implement exponential backoff; share rate limit state across pipeline runs; log wait time and continue — never fail the pipeline.

---

## 20. Non-Goals for MVP

Not building: real-time dashboards, mobile app, multi-language UI (Hindi/Tamil), custom brand tracking, user accounts, team collaboration, third-party API access, automated notifications, historical data > 90 days, categories beyond Consumer Tech, predictive ML beyond AI API, custom report templates, white-label, CRM/Slack integrations, fine-tuned models, paid data sources.

**MVP is complete when:** A brand manager opens the dashboard Monday morning, reads the weekly pulse in 10 minutes, and walks into a strategy meeting with three genuine insights and one clear recommendation — all grounded in real Indian consumer signals, generated without human analyst involvement.

---

## 21. Current MVP Stack (Overrides Earlier Sections Where Conflict)

- **Development environment:** Claude Code
- **Scraping:** Apify Ultimate Scraper — preferred scraping layer

All scraped data must be normalized into:
```
date, source, category, brand, topic, url, author, text, engagement, raw_metadata
```

- **AI Gateway:** OpenRouter API — all AI calls go through `ai/openrouter_client.py`

  Do not call OpenRouter directly from `app.py` or any dashboard file.

  Default: `OPENROUTER_MODEL=openrouter/auto`

- **Dashboard:** Streamlit
- **Storage:** CSV first → Google Sheets when needed
- **Orchestration:** n8n only after MVP is validated

**Cost discipline:** Scrape small batches → remove duplicates → batch AI calls → cache outputs → cheap models for classification → strong models only for final summaries.

---

*Last updated: 2026-05-10 | Version: 1.0.0 | Owner: Solo Founder | Review: Monthly or at major milestones*
