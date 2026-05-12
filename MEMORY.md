# MEMORY.md — India Consumer Pulse AI
## Long-Term Project Memory & Strategic Context

> This file is the persistent strategic memory of the project. It captures founder context, product decisions, philosophical principles, and directional choices that should inform every development session. Claude Code reads this alongside CLAUDE.md to maintain continuity across sessions.

---

## 1. Project Summary

**Project Name:** India Consumer Pulse AI

**One-line description:** An AI-powered consumer intelligence platform that listens to Indian digital conversations and converts them into strategic business intelligence — the kind that a senior consumer strategist would produce, not a dashboard tool.

**Core purpose:** To give Indian brands, founders, and strategists access to real-time, AI-generated consumer narrative intelligence that currently requires expensive agencies, slow surveys, or generic global tools that miss Indian market nuance.

**What makes this different from social listening tools:** This platform interprets consumer conversations through a strategic lens. It does not just count mentions or measure sentiment. It identifies dominant narratives, trend trajectories, unmet needs, and brand positioning opportunities — and outputs them in the language of business strategy, not data science.

**Current status:** MVP under active development. Category focus: Consumer Tech in India.

**Target delivery:** A working dashboard delivering weekly Consumer Tech intelligence, demo-ready for potential enterprise clients.

**North star:** Become the go-to AI-powered consumer intelligence platform for Indian brands — the Bloomberg Terminal of Indian consumer understanding.

---

## 2. Founder Background

**Name:** Pooja Kapoor (inferred from email context)

**Experience:**
- 18 years in market research and consumer insights
- Deep expertise in brand tracking — tracking methodologies, equity frameworks, brand health monitors
- Strong analytics background: R, SPSS, Power BI, Python
- Experience interpreting quantitative and qualitative consumer data for brand strategy
- Consulting mindset — used to translating research into board-level recommendations
- Strong strategic storytelling: the ability to convert complex data into a clear, compelling narrative for decision-makers
- Deep, intuitive understanding of Indian consumers — their price psychology, aspirations, platform behavior, cultural logic, and brand relationships

**Current growth areas:**
- GenAI tools and APIs (Claude, OpenAI)
- Agentic AI systems (Claude Code, n8n-based automation)
- Multi-agent pipeline design
- Python scripting for data pipelines
- Prompt engineering for consumer intelligence

**Founder archetype:** Experienced research-and-strategy professional who is now applying AI to automate and scale what she has spent 18 years doing manually as a consultant.

**Critical implication for the platform:** The AI system must produce outputs that meet the founder's own high standard for consumer insight quality. The founder will immediately recognize if insights sound shallow, generic, or analytically weak. The system must produce insights that she would be proud to put her name on.

---

## 3. Founder Strengths

These strengths must be reflected in the platform's outputs and design choices:

**Strategic framing:** Insights are always positioned in terms of brand strategy and business implication, not raw observation. The platform must generate the "so what" — not just the "what."

**Narrative construction:** 18 years of research writing means the founder knows the difference between a data summary and a compelling consumer narrative. Outputs must tell a coherent story, not list findings.

**Brand tracking expertise:** The founder understands brand equity dimensions, brand health tracking, competitive positioning, and how consumer perception shifts over time. Brand intelligence modules must reflect this sophistication.

**Consultant mentality:** Research must be decision-ready. Every output is framed as if it will be presented to a CMO or marketing director. No jargon without explanation. No finding without implication.

**Indian market intuition:** The founder has an instinctive feel for what Indian consumers value, how they communicate online, and how their stated preferences differ from their actual purchase behavior. Prompts and insight frameworks must encode this intuition.

**Analytical rigor:** Years of working with quantitative data means the founder values evidence-based claims and is skeptical of vague generalizations. Every AI-generated insight must be grounded in source signals.

**Storytelling:** Reports must be readable by a busy brand manager in under 10 minutes. Dense, jargon-heavy outputs are a failure mode.

---

## 4. Product Positioning

**Positioning statement:**
India Consumer Pulse AI is the strategic intelligence layer that Indian brands have been missing — an AI-powered platform that converts the noise of digital conversation into the signal of consumer narrative, built by someone who has spent 18 years understanding what Indian consumers actually mean when they speak.

**Category:** Consumer Intelligence / AI-Powered Market Research

**Competitive frame:**
- Against global social listening tools (Brandwatch, Sprinklr, Mention): "Built for India, not retrofitted for it."
- Against traditional market research agencies: "Weeks of fieldwork, compressed into Monday morning intelligence."
- Against generic AI chatbots used for research: "Structured, auditable intelligence — not a chatbot conversation."
- Against DIY Python dashboards: "Strategic interpretation, not raw data."

**Positioning pillars:**
1. **India-native** — Every signal, every prompt, every output is designed for the Indian market context
2. **Narrative-first** — Consumer intelligence as strategic story, not sentiment score
3. **Actionable** — Every insight ends with a business implication or recommended action
4. **Affordable** — Enterprise-quality intelligence at D2C-startup pricing
5. **AI-powered, human-calibrated** — Built by a senior consumer insights professional, scaled by AI

**Tone of the platform:**
Authoritative but accessible. Analytical but not cold. Strategic but not abstract. The platform should feel like having a smart, experienced consumer strategist on call at all times.

---

## 5. Current MVP Scope

**Category:** Consumer Tech India

**Subcategories:**
- Smartphones
- Wearables (TWS, smartwatches, fitness bands)
- Laptops & PCs
- Audio (headphones, Bluetooth speakers)
- Smart Home

**Data Sources (MVP):**
- Reddit India (r/india, r/indiangaming, r/TechDeals, r/oneplus, r/samsung, r/xiaomi, r/suggestalaptop)
- Twitter/X (India consumer tech conversations, brand mentions)
- Google Play Store reviews (top Consumer Tech apps and devices)

**Output format (MVP):**
- Streamlit dashboard with 5 pages
- Weekly pulse report (AI-generated narrative)
- PDF export of weekly report
- Google Sheets data store (interim database)

**Delivery cadence:**
- Daily data ingestion and AI processing
- Weekly insight aggregation and report generation
- Monthly strategic synthesis (optional in MVP)

**Success definition for MVP:**
The dashboard delivers a weekly Consumer Tech intelligence brief that a brand manager finds genuinely useful — with zero human analyst involvement in the generation process.

**Timeline:** MVP demo-ready within 60 days of build start.

---

## 6. Categories Planned

The platform is designed to be category-agnostic. Every category is added as a configuration layer, not a code rewrite.

| Phase | Category | Rationale |
|---|---|---|
| 1 (MVP) | Consumer Tech | High digital conversation volume, strong Reddit/Twitter presence, clear brand landscape |
| 2 | EV (Electric Vehicles) | Massive category growth, high consumer anxiety and aspiration, brand trust critical |
| 2 | FMCG | Large TAM, D2C brand explosion, price sensitivity dynamics unique to India |
| 2 | Wellness | Post-COVID category growth, aspirational + functional tension, Ayurveda vs modern |
| 3 | Retail | E-commerce vs offline tension, hyperlocal dynamics, consumer loyalty patterns |
| 3 | Finance | Fintech adoption, UPI culture, insurance and investment sentiment |
| 3 | QSR | Delivery platform dynamics, value vs experience tension, regional taste preferences |
| 4 | Beauty | Skin tone diversity awareness, K-Beauty influence, D2C brand explosion |

**Taxonomy rule:** When adding a new category, only `config/categories.yaml` and `config/sources.yaml` need updates. The pipeline, AI layer, and dashboard are category-agnostic by design.

---

## 7. Current Category Focus

### Consumer Tech — Deep Context

**Why Consumer Tech first:**
- Highest digital conversation volume among Indian consumers
- Reddit India has highly engaged tech communities
- Clear, well-defined brand landscape (Apple, Samsung, OnePlus, boAt, Noise, Xiaomi, etc.)
- Founder likely has research experience in this category
- Fast-moving category where weekly intelligence has obvious value
- B2B buyer for this insight (brand managers at Consumer Tech companies) is easy to identify

**Key brand dynamics in Indian Consumer Tech:**
- Apple: Aspirational anchor. Status symbol. Growing but still premium-only.
- Samsung: Legacy trust + premiumization push. Galaxy A series as mass-market workhorse.
- OnePlus: Premium promise that drifted. Community loyalty vs. product portfolio confusion.
- Xiaomi/Mi: Value king facing brand trust erosion. Quality perception challenge.
- Realme/OPPO/Vivo: Feature-rich at mid-range. Youth-first positioning.
- boAt/Noise: Indian D2C audio success story. Price-performance narrative.
- iQOO: Emerging performance brand. Gaming-first identity.
- Nothing: Cult design appeal. Premium accessory aesthetic.

**Key consumer narratives to track in Consumer Tech:**
- Premium vs. value tension (always present)
- Made-in-India sentiment (PLI scheme, brand nationalism)
- After-sales service quality (major pain point across brands)
- Camera wars (primary upgrade driver for mass market)
- Battery anxiety (especially for wearables and laptops)
- EMI affordability and no-cost EMI availability
- Flipkart vs. Amazon India pricing wars
- Trade-in and upgrade culture
- E-waste and sustainability consciousness (emerging)

---

## 8. Core Consumer Insight Philosophy

This philosophy governs every AI-generated output. These are non-negotiable principles.

**The platform interprets, not just observes.**
Raw data says: "43% of posts mention battery life."
Insight says: "Battery anxiety is now the primary reason Indian consumers delay upgrading their TWS earbuds — not price. The category's next battleground is power management communication, not feature stacking."

**The platform finds narrative, not just themes.**
A theme is a topic. A narrative is a story with a protagonist (the consumer), a tension (what they want vs. what they have), and a direction (where this is heading). Every weekly pulse has a dominant narrative.

**The platform is always India-specific.**
Generic consumer insight has no value here. Every finding must be grounded in the specific context of Indian consumers: their income constraints, their aspirational logic, their trust hierarchies, their festival-linked purchase psychology, their Hinglish expression, their platform preferences.

**The platform speaks to the decision-maker.**
The user of this platform is a CMO, brand manager, or founder. They do not want to see a data table. They want to know: "What does this mean for my brand? What should I do about it?"

**The platform is honest about confidence.**
If the data is thin, the insight says so. If the signal is early-stage, it is labeled "emerging." If the AI cannot ground an insight in source data, it does not generate that insight.

**The platform generates insight units, not insight atoms.**
An insight unit = observation + interpretation + implication + recommendation.
An insight atom = "43% of posts are negative." (Not useful alone.)

---

## 9. Key Differentiators

**D1: India-first design**
Not built for a global market with India as a filter. Every prompt, every data source selection, every taxonomy decision is optimized for India's unique digital and consumer landscape.

**D2: Senior analyst voice**
The AI writes like a senior consumer strategist with 15+ years of experience — not like a generic summarizer. The platform is calibrated by someone who knows what great consumer insight sounds like.

**D3: Narrative intelligence**
Other tools measure. This platform interprets. The difference is the strategic value between "here is the data" and "here is what the data means for your brand."

**D4: Category-agnostic modularity**
New categories are configuration, not code. This allows rapid expansion without technical debt.

**D5: Actionability built in**
Every insight output mandates a "strategic implication" or "recommended action" field. No insight is complete without it.

**D6: Founder credibility**
Built by someone with 18 years of consumer research experience. This is not a tech company that wandered into insights. This is an insights expert who has leveraged AI to scale her craft.

**D7: Affordable intelligence**
Enterprise social listening tools cost $2K-$10K/month. This platform delivers strategic intelligence at a fraction of the cost — a major advantage in the Indian B2B market where budget sensitivity is real.

---

## 10. Important Product Decisions

These decisions have been made and should not be relitigated without strong new evidence:

**Decision 1: Weekly cadence for insights (not real-time)**
Rationale: Real-time dashboards create noise addiction, not strategic value. A weekly pulse forces aggregation into meaningful narrative. Real-time is a Phase 3 feature.

**Decision 2: Streamlit for MVP dashboard (not custom React)**
Rationale: Solo founder, speed matters, Streamlit is sufficient for proof-of-concept with enterprise clients. React is a Phase 2/3 upgrade.

**Decision 3: Google Sheets as interim database**
Rationale: Zero infrastructure cost, easy to inspect and audit manually, sufficient for MVP data volumes. Upgrade path to Supabase/PostgreSQL is documented.

**Decision 4: Claude API as primary AI model**
Rationale: Best-in-class for nuanced narrative generation, long-context analysis, and instruction-following. Aligns with the founder's existing tooling familiarity.

**Decision 5: No real-time scraping — scheduled pipeline only**
Rationale: Reduces cost, simplifies infrastructure, avoids rate-limit emergencies. The pipeline runs nightly; insights are fresh enough for weekly strategic use.

**Decision 6: No user accounts in MVP**
Rationale: Single-founder tool. Authentication complexity adds zero value at this stage.

**Decision 7: Narrative output over charts-first design**
Rationale: The value proposition is interpretation, not visualization. Charts support the narrative; they do not replace it.

**Decision 8: n8n for orchestration (not Airflow)**
Rationale: Visual pipeline editor, no-code triggers, free self-hosted option, sufficient for MVP pipeline complexity. Airflow is overkill at this stage.

**Decision 9: English + Hinglish (not full multi-language)**
Rationale: English-medium and Hinglish content dominates the target data sources (Reddit, Twitter/X) for the Consumer Tech category. Full Hindi/regional language NLP is Phase 3.

**Decision 10: AI-generated insight sections + AI-composed report narrative**
Rationale: The platform's differentiation is in the quality of AI-written interpretation. Human editing of outputs is not in the workflow — the system must generate publishable output autonomously.

---

## 11. Technical Stack Decisions

| Decision | Chosen Tool | Why | Upgrade Path |
|---|---|---|---|
| Language | Python 3.11+ | Universal, large ecosystem, founder familiarity | — |
| AI model | Claude (Sonnet) | Best narrative quality, long context, reliable JSON output | Haiku for cheap tasks, Opus for synthesis |
| Dashboard | Streamlit | Fast to build, free hosting, sufficient for MVP | React + Next.js at scale |
| Orchestration | n8n | Visual, free, easy for solo founder | Prefect / Airflow |
| Database | Google Sheets | Free, auditable, no setup | Supabase → PostgreSQL |
| Deployment | Streamlit Cloud | Free tier, zero DevOps | AWS / GCP |
| PDF export | ReportLab / WeasyPrint | Python-native, no external service | Puppeteer |
| Monitoring | Google Sheets log | Free, visible, good enough | Grafana / Datadog |
| Secrets | .env + Streamlit secrets | Simple, sufficient | AWS Secrets Manager |
| Testing | pytest | Standard, sufficient | — |

**Stack philosophy:** Choose the cheapest sufficient tool. Never let infrastructure complexity become an obstacle to insight quality. Upgrade when the current tool becomes the bottleneck.

---

## 12. Workflow Architecture

### Daily Intelligence Pipeline

```
00:30 IST — n8n triggers daily pipeline
  → Python: Ingest posts from Reddit, Twitter/X, Play Store
  → Python: Clean, deduplicate, tag with category/subcategory
  → Python: Batch and send to Claude API for analysis
  → Python: Store structured insight records in Google Sheets

07:00 IST Monday — n8n triggers weekly report pipeline
  → Python: Aggregate 7 days of insight records
  → Python: Build trend rankings, narrative clusters, brand scores
  → Python: Send aggregated data to Claude API for narrative generation
  → Python: Write report sections to Google Sheets / JSON
  → Streamlit: Dashboard refreshes automatically on next load
```

### Data Flow

```
[Reddit / Twitter / Play Store]
          ↓ (raw JSON)
[Ingestion Layer — Python]
          ↓ (cleaned, tagged records)
[Preprocessing Layer — Python]
          ↓ (validated, deduplicated)
[AI Analysis Layer — Claude API]
          ↓ (structured insight JSON)
[Google Sheets — Insight Store]
          ↓ (aggregated weekly)
[AI Narrative Layer — Claude API]
          ↓ (narrative sections, recommendations)
[Streamlit Dashboard]
          ↓ (user-facing)
[Brand Manager / Founder]
```

### Key Workflow Principles

- The pipeline is idempotent — running it twice does not create duplicate insights
- Every pipeline run is logged with: source counts, AI token usage, cost estimate, errors
- The dashboard never calls the AI API directly — all AI work happens in the pipeline
- Google Sheets serves as both database and audit trail in MVP

---

## 13. Prompt Engineering Philosophy

**Core premise:** A prompt is a research instrument. The quality of the prompt determines the quality of the insight. This must be approached with the same rigor as designing a research questionnaire.

**The founder's 18 years of research experience must be encoded into prompts.** This means prompts must contain:

- **Domain framing:** Tell Claude it is an expert in Indian consumer intelligence, not a generic analyst
- **Cultural context:** Explicitly state Indian market nuances (price sensitivity, aspirational buying, festival cycles, Hinglish discourse)
- **Audience specification:** Tell Claude who will read the output (CMO, brand manager, founder)
- **Quality bar:** Describe what a great insight looks like vs. a weak one
- **Hallucination guard:** Explicitly instruct Claude to only report what is present in the data
- **Output structure:** Always specify JSON schema for pipeline outputs; prose format for reports
- **Tone guide:** Strategic, authoritative, India-specific, accessible to a non-researcher

**The "senior strategist" test:** Before deploying any prompt, ask: "Would a senior consumer strategist be embarrassed by this output?" If yes, revise the prompt.

**Prompt versioning:** Every prompt is versioned. v1 is the starting point. Every significant change creates v2, v3, etc. Old versions are archived.

**Temperature settings:**
- Analytical tasks (sentiment, topic extraction): 0.2-0.3 (consistency)
- Narrative synthesis (trend stories, brand narratives): 0.5-0.6 (creativity within bounds)
- Strategic recommendations: 0.4 (balanced)
- Report writing: 0.6-0.7 (fluent, engaging prose)

---

## 14. Research Methodology Principles

These principles reflect the founder's 18-year research background and must be embedded in how the AI system processes and interprets consumer data.

**Principle 1: Volume + Intensity, not volume alone**
High volume of mentions is not the same as high importance. A small cluster of intensely emotional posts about a product failure is more strategically important than a large cluster of casual mentions.

**Principle 2: Stated vs. revealed preference**
Consumers often say they want one thing and buy another. The platform must flag when stated preferences (what people say they want) appear to diverge from purchase behavior signals (what people say they actually bought).

**Principle 3: Latent need identification**
The most valuable insight is not what consumers complain about directly — it is the underlying need that complaint reveals. Prompt engineering must explicitly target latent need identification.

**Principle 4: Brand equity dimensions**
When analyzing brand intelligence, use classic brand equity dimensions as the interpretive lens:
- Awareness (are people talking about the brand?)
- Quality perception (what quality signals are present?)
- Differentiation (what makes this brand distinct in consumer language?)
- Value for money (how is the brand positioned on the price-value spectrum?)
- Trust (what trust signals or breaches are present?)
- Loyalty intent (are current users intending to stay or switch?)

**Principle 5: Competitive positioning**
Brand intelligence is only meaningful in competitive context. Always interpret a brand's performance relative to its stated and implied competitors in the Indian market.

**Principle 6: Trend lifecycle awareness**
Every trend has a lifecycle: emerging → gaining → mainstream → peaking → declining. The platform must not just identify trends but place them on this lifecycle curve, because the strategic response differs by stage.

**Principle 7: Price tier context**
Never interpret consumer sentiment without tagging it to the relevant price tier. A sentiment about battery life in ₹1,500 earbuds is a different signal than the same sentiment in ₹15,000 headphones.

---

## 15. Insight Writing Style

**Voice:** A senior consumer strategist writing a brief for a CMO.

**Tone attributes:**
- Authoritative but not arrogant
- Specific but not technical
- Evidence-based but not data-heavy
- Interpretive but not speculative
- India-aware in every sentence

**Structural formula for an insight unit:**

```
[HEADLINE — bold, one sentence, contains the "so what"]

[CONTEXT — 1-2 sentences setting up the observation]

[FINDING — 2-3 sentences describing what the data shows, 
  with source volume indicator]

[INTERPRETATION — 2-3 sentences explaining WHY this is happening,
  with reference to Indian consumer behavior logic]

[IMPLICATION — 1-2 sentences on what this means strategically 
  for brands in this category]

[RECOMMENDATION — 1 concrete action a brand manager can take]
```

**Writing anti-patterns to avoid:**
- "Consumers are talking about X." (Observation without interpretation — useless)
- "There is a trend towards X." (Vague — which trend? Why? By how much?)
- "X% of posts mention Y." (Data without meaning)
- "Brands should focus on X." (Too vague — which brands? What specifically?)
- "In conclusion, X is important." (Filler language — never use in insights)

**Writing patterns to use:**
- "Indian consumers in the ₹15K-25K smartphone segment are now framing camera quality as a hygiene factor, not a differentiator — the battleground has shifted to software experience and update longevity."
- "The boAt-Noise rivalry is no longer about price — it is about which brand can establish deeper lifestyle credibility with the 18-25 urban Indian cohort."
- "OnePlus faces a narrative crisis: its core users (who bought into 'Never Settle') feel the brand has settled — a loyalty gap that competitors are actively exploiting."

---

## 16. Dashboard Design Preferences

**Mental model for the dashboard:** A Monday morning intelligence briefing, not a self-service analytics tool.

**Design preferences (based on founder background as a consultant and researcher):**

- **Narrative panels over chart grids** — Lead with the story, support with data
- **Confidence indicators visible** — The founder's research background means she values knowing how much to trust an insight
- **Source transparency** — Every insight should indicate its data volume basis (e.g., "based on ~85 posts")
- **Week-over-week change** — Always show direction, not just current state
- **No pie charts for sentiment** — Too reductive. Use diverging bars or qualitative scale instead
- **Brand comparison in competitive context** — Not individual brand scorecards in isolation
- **Actionable callouts** — Highlighted recommendation boxes at the end of every section
- **Executive summary page first** — The CMO-ready view before the analytical detail
- **Exportable report** — PDF export of the weekly pulse for sharing with clients or teams

**Color philosophy:**
- Navy (authority and depth) for primary chrome
- Signal red for alerts, sharp trend shifts, and urgency callouts
- Growth green for positive momentum
- Neutral grey for data context
- Never use traffic-light (red/amber/green) in a simplistic way — Indian consumer signals are nuanced

**Page load philosophy:** Pre-generate all AI outputs in the pipeline. The dashboard should load and display results, never trigger AI generation on page load. Speed and reliability matter.

---

## 17. AI Narrative Generation Rules

These rules govern how Claude generates the narrative sections of weekly reports and insight cards.

**Rule 1: Ground every claim**
Claude must only assert trends or narratives that are supported by the input data. The prompt explicitly forbids inferring trends not present in the source records.

**Rule 2: Name the consumer**
Every narrative must identify the consumer segment it is describing. Not "Indian consumers" as a monolith. "Urban Indian millennial smartphone buyers in the ₹20K-35K segment" is specific and useful.

**Rule 3: Articulate the tension**
Every strong consumer narrative has a central tension — what consumers want vs. what they are getting, or what a brand promises vs. what it delivers. Claude must identify and name this tension.

**Rule 4: Locate the inflection point**
Is this narrative new, accelerating, or entrenched? Claude must assess where the narrative sits on its lifecycle and communicate this in the output.

**Rule 5: India-specific causality**
When explaining why a consumer narrative exists, Claude must invoke India-specific factors where relevant: festival buying cycles, price tier dynamics, service infrastructure gaps, made-in-India sentiment, EMI culture, youth aspiration patterns.

**Rule 6: End with forward direction**
Every narrative section must end with a forward-looking statement: "This narrative is likely to intensify as..." or "The inflection point will come when..."

**Rule 7: Confidence disclosure**
If the supporting data volume is low (<15 records), the narrative must be prefaced with "Early signal:" or "Emerging narrative:" to signal lower confidence.

**Rule 8: Strategic implication always last**
The final sentence of every insight section must be a strategic implication or action direction. Never end on pure observation.

---

## 18. Strategic Interpretation Guidelines

The platform is built by a consultant. Outputs must reflect consultant-grade strategic interpretation.

**The consultant's interpretation framework applied to consumer intelligence:**

**Step 1 — Observe:** What is actually in the data?
**Step 2 — Cluster:** What themes or patterns emerge from the observations?
**Step 3 — Interpret:** Why is this pattern happening? What consumer psychology or market dynamic explains it?
**Step 4 — Contextualize:** What India-specific factors amplify or modify this interpretation?
**Step 5 — Extrapolate:** If this continues, where does it lead in 3-6 months?
**Step 6 — Implicate:** What does this mean for brands in this space?
**Step 7 — Recommend:** What should a brand manager do, and by when?

**This 7-step process is embedded in every insight-generation prompt.** The AI is instructed to work through these steps, even if the output only shows steps 3-7 (the interpretation and action layer).

**Strategic frame categories:**
When interpreting consumer intelligence, always consider which strategic frame applies:
- **Brand positioning frame:** How does this signal affect how brands should position vs. competitors?
- **Product strategy frame:** What does this signal mean for product development priorities?
- **Marketing message frame:** What communication strategy does this signal recommend?
- **Channel strategy frame:** Does this signal suggest shifts in where/how consumers buy?
- **Pricing strategy frame:** What does this reveal about price sensitivity and value perception?
- **Innovation frame:** What unmet need or market gap does this signal reveal?

---

## 19. Consumer Trend Detection Logic

**Trend vs. noise distinction** is the most important technical challenge in consumer intelligence. The platform must not cry wolf on every spike in conversation volume.

**A trend is only a trend when it shows:**

1. **Volume threshold:** Minimum 15+ posts/comments discussing the topic within a 7-day window
2. **Cross-source corroboration:** The signal appears in at least 2 different data sources (e.g., Reddit + Twitter, or Reddit + app reviews)
3. **Temporal acceleration:** Volume is growing week-over-week, not stable or declining
4. **Semantic consistency:** Posts are discussing the same underlying topic, not different topics that share a keyword
5. **Sentiment signal:** Strong sentiment (positive or negative) accompanies the volume signal — neutral high-volume is category noise, not trend

**Trend lifecycle labels:**
- `EMERGING` — Signal detected in 1 source, <20 posts, <2 weeks old
- `GAINING` — Signal in 2+ sources, 20-100 posts, 2-4 weeks old, accelerating
- `MAINSTREAM` — Signal in 2+ sources, >100 posts, widely discussed, sentiment settling
- `PEAKING` — Volume growth slowing, signal still high, early decline indicators
- `DECLINING` — Volume falling, conversation moving on
- `CYCLICAL` — Recurring signal (e.g., festival sale discussions, budget phone season)

**The platform must communicate the lifecycle stage with every trend, because the strategic response differs at each stage.**

A brand that enters an `EMERGING` trend has a first-mover window.
A brand that reacts to a `DECLINING` trend is wasting resources.

**Trend types to track:**

| Type | Example | Strategic Value |
|---|---|---|
| Product narrative trend | "Indian consumers are now prioritizing repairability" | Product strategy |
| Brand narrative trend | "OnePlus is losing its premium story" | Brand positioning |
| Category trend | "The TWS market is commoditizing at ₹1,500" | Market entry/exit |
| Consumer behavior trend | "Indians are buying refurbished flagships more" | Channel and pricing |
| Cultural trend | "Made in India as a purchase trigger" | Campaign strategy |
| Crisis signal | "Series of service failure stories about Brand X" | Reputation management |

---

## 20. Future AI Agents Planned

The platform will evolve into a multi-agent intelligence system. These agents are planned:

**Agent 1: The Trend Scout Agent**
- Monitors incoming data streams for emerging signals
- Flags anomalies: volume spikes, new topic clusters, sudden sentiment shifts
- Output: daily alert log of noteworthy signals
- Trigger: runs every 4 hours on new ingested data

**Agent 2: The Brand Tracker Agent**
- Maintains a running brand perception model for configured brands
- Tracks: share of voice, sentiment trajectory, association themes, competitive positioning
- Flags: sudden reputation shifts, competitive moves, brand crisis signals
- Output: weekly brand health score with narrative explanation

**Agent 3: The Narrative Builder Agent**
- Reads outputs from Trend Scout and Brand Tracker
- Constructs the dominant consumer narrative for the week
- Identifies the central tension, consumer protagonist, and direction of travel
- Output: weekly narrative brief (3-5 paragraphs, written in strategic prose)

**Agent 4: The Pain Point Extractor Agent**
- Specialized in finding friction, frustration, unmet needs, and latent desires
- Goes deeper than surface sentiment — looks for the root cause of consumer pain
- Tracks pain points over time to identify whether issues are being resolved or worsening
- Output: ranked pain point matrix with trend arrows and evidence clusters

**Agent 5: The Recommendation Agent**
- Reads all other agent outputs
- Applies the founder's strategic interpretation framework
- Generates 3-5 prioritized, evidence-backed strategic recommendations
- Each recommendation includes: confidence level, time sensitivity, and likely ROI frame
- Output: strategic recommendation brief

**Agent 6: The Orchestrator Agent**
- Manages the workflow of all other agents
- Resolves conflicting signals between agents
- Ensures the final weekly brief is internally consistent
- Maintains the shared intelligence context across agents

**Implementation timeline:**
- MVP: Single-model sequential pipeline (no agents)
- Phase 2: Trend Scout + Brand Tracker as separate pipeline stages
- Phase 3: Narrative Builder + Orchestrator
- Phase 4: Full 6-agent system with human-in-the-loop review option

---

## 21. Scalability Notes

**The core scalability principle:** The platform is built category-agnostic from day one. Adding a new category (e.g., EV, FMCG) should require no new Python code — only configuration changes.

**What scales with configuration only:**
- New categories and subcategories (categories.yaml)
- New brands to track (categories.yaml)
- New data sources (sources.yaml)
- New prompt versions (config/prompts/)
- New keyword sets for taxonomy (categories.yaml)

**What requires code changes to scale:**
- New data source types (e.g., adding Instagram as a source)
- New insight types (e.g., adding a "regulatory risk" signal type)
- New output formats (e.g., API endpoint for client integration)
- New dashboard pages beyond the 5 MVP pages

**Infrastructure scaling triggers:**
| Trigger | Action |
|---|---|
| >50K records/week | Migrate from Google Sheets to Supabase |
| >$50/month AI cost | Introduce model tiering (Haiku for classification) |
| >3 categories live | Move orchestration from n8n to Prefect |
| First paying client | Move to Supabase Auth and per-tenant data isolation |
| >10 paying clients | API layer (FastAPI) for enterprise integrations |
| >50 paying clients | Infrastructure on AWS/GCP, Airflow, dedicated support |

**The solo founder constraint:** Every architectural decision must be executable by a solo founder with growing technical skills. Avoid architectures that require a DevOps team to maintain.

---

## 22. Cost Constraints

**Hard constraint:** Total monthly cost must stay under $50 during MVP phase.

**Cost allocation:**
- Claude API: target ~$15-25/month (primary cost driver)
- Twitter API Basic tier: $0 (free basic access) or ~$100/month if basic is insufficient
- Reddit API: $0 (free developer tier)
- Streamlit Cloud: $0 (free tier, up to 3 apps)
- n8n self-hosted: $0 (Oracle Cloud always-free instance)
- Google Sheets API: $0 (free)

**Cost optimization strategies in priority order:**

1. **Batch aggressively:** 15-20 posts per Claude API call (not 1 per call)
2. **Cache generously:** Store AI analysis results; never re-analyze the same content
3. **Model-tier appropriately:** Haiku for classification, Sonnet for insights, Sonnet for reports
4. **Token budget tightly:** Set max_tokens per task type; never use unlimited
5. **Filter before analyzing:** Remove spam, very short posts, and duplicate content before sending to Claude
6. **Schedule off-peak:** Run heavy AI processing at night to avoid rate limit issues
7. **Deduplicate ruthlessly:** Same content from different sources counts once, not twice

**Cost monitoring:** Every pipeline run logs token usage and estimated cost to Google Sheets. A simple weekly sum tells the founder exactly what was spent.

**Cost escalation protocol:** If a single pipeline run costs >$5, log a critical alert and investigate before the next run.

---

## 23. Future Monetization Possibilities

These are possibilities for consideration when MVP proves value. Not commitments.

**Model 1: B2B SaaS Subscription**
Monthly subscriptions by category and feature tier.
- Starter: ₹4,999/month (1 category, weekly pulse, 3-brand tracking)
- Professional: ₹14,999/month (2 categories, daily pulse, custom brands, exports)
- Enterprise: Custom (all categories, white-label, API access, dedicated support)

**Target revenue by phase:**
- MVP: 0 (validation only)
- Phase 1: ₹1-2L/month (2-4 pilot clients)
- Phase 2: ₹5-10L/month (10-20 clients)
- Phase 3: ₹20-50L/month (50+ clients, enterprise deals)

**Model 2: Report Licensing**
Sell monthly category intelligence reports to multiple buyers.
- "India Consumer Tech Pulse" — monthly PDF report, sold at ₹25K/month per subscriber
- Like a research syndication model (similar to Euromonitor or Kantar annual reports)

**Model 3: Consulting + AI**
Use the platform to power consulting engagements. Charge for bespoke analysis using the underlying intelligence infrastructure. Higher margin, lower scale.

**Model 4: Enterprise API**
When the platform has proven accuracy, sell API access for brands to embed intelligence in their own dashboards. Premium tier, volume-based pricing.

**Model 5: VC/Investor Reports**
Quarterly sector intelligence sold to VC firms and PE funds doing India consumer investment research.

**Preferred path for the solo founder:** Start with Model 3 (consulting + AI) to generate early revenue and validate insight quality with real clients. Transition to Model 1 (SaaS) as the platform matures and can be self-serve.

---

## 24. Important Things To Avoid

These are anti-patterns, failure modes, and philosophical wrong turns that must be actively avoided.

**Anti-pattern 1: Sentiment dashboard thinking**
The platform is NOT a sentiment dashboard. Avoid building anything that leads with "63% positive / 27% negative / 10% neutral." This is the lowest form of consumer intelligence and does not reflect the platform's value proposition.

**Anti-pattern 2: Data without interpretation**
Never surface raw numbers, charts, or tables without accompanying strategic narrative. Every quantitative element must have a qualitative framing.

**Anti-pattern 3: Generalizing "Indian consumers"**
India is not one consumer. Never write "Indian consumers prefer X" without specifying the segment, price tier, region, or demographic. Generalization is an intellectual failure in this context.

**Anti-pattern 4: Chasing real-time**
Real-time is expensive, technically complex, and often produces noise, not signal. The weekly pulse model is deliberate. Do not add real-time features until the weekly model is proven.

**Anti-pattern 5: Building for hypothetical users**
Build for the specific primary user (brand manager in Consumer Tech). Do not add features for hypothetical future user types before the primary user is well-served.

**Anti-pattern 6: Over-engineering the data layer**
Google Sheets is sufficient for MVP. Do not spend time building a production database before there is data worth storing. Infrastructure should follow product-market fit, not precede it.

**Anti-pattern 7: AI outputs without validation**
Never display Claude API outputs to the user without schema validation and basic quality checks. Hallucinated brand names, fabricated statistics, or malformed JSON must be caught in the pipeline, not on the dashboard.

**Anti-pattern 8: Prompt stagnation**
Prompts must evolve. If a prompt is producing outputs that feel shallow or generic, it must be revised. Treat prompts as living research instruments, not set-and-forget configuration.

**Anti-pattern 9: Ignoring Indian platform specificity**
Reddit and Twitter are not the same in India as they are globally. r/india has specific community norms; Indian Twitter/X has heavy political overlay. Platform-specific filtering and weighting must be applied.

**Anti-pattern 10: Building features before validating insights**
The platform's value lives in the quality of its insights, not the sophistication of its feature set. Prioritize insight quality over feature quantity always.

---

## 25. Future Vision

**3-year vision:**

India Consumer Pulse AI becomes the default intelligence layer for Indian brands making category, positioning, and consumer strategy decisions. It is used daily by:
- Brand managers at mid-to-large Indian consumer brands
- CMOs at D2C startups
- Strategy teams at advertising and marketing agencies
- VC analysts tracking consumer sector investments
- Category heads at major Indian retail chains

**5-year vision:**

The platform expands beyond consumer intelligence into a full **Decision Intelligence System** — where the AI not only interprets consumer signals but actively recommends, simulates, and tracks the outcomes of brand and product decisions in the Indian market.

Capabilities at 5 years:
- All 8 consumer categories fully live and calibrated
- Real-time trend alert system with < 4-hour signal detection
- Longitudinal brand health tracking (18-month history minimum)
- Natural language query interface: "What happened to OnePlus perception last quarter?"
- Predictive narrative modeling: "Based on current signals, here is what will happen to X category in the next 60 days"
- White-label SaaS for research agencies to deploy under their own brand
- Multi-market expansion: start with India, expand to Indonesia, Vietnam, Nigeria

**The ultimate form of this platform:**

An AI system that has internalized 18 years of consumer research expertise, knows the Indian market as deeply as a seasoned local analyst, updates itself daily from thousands of real consumer signals, and delivers strategic intelligence at the quality of a top-tier consulting firm — to any brand that needs it, at a price they can afford.

**This is the mission. Build accordingly.**

---

## Updated Technical Direction

The project will use Apify Ultimate Scraper and OpenRouter API for the first MVP.

Reason:
This gives the founder maximum flexibility with minimum cost and avoids locking into one scraping source or one AI model.

## Current MVP Flow

Keyword input → Apify scrape → CSV storage → OpenRouter classification → Streamlit dashboard → downloadable report

## Current Priority

Build a local working demo first.

Do not overbuild:
- user login
- payment system
- database backend
- full SaaS architecture
- complex multi-agent orchestration

These can come later.

## First Category

Consumer Tech India.

Initial focus:
- AI laptops
- premium laptops
- smartphone upgrades
- brand conversations around Apple, Lenovo, HP, Dell, ASUS

---

*Document version: 1.1*
*Created: 2026-05-10*
*Owner: Pooja Kapoor — Founder, India Consumer Pulse AI*
*Review cadence: Update after every major product milestone or strategic pivot*
*Companion document: CLAUDE.md (engineering standards and technical architecture)*
