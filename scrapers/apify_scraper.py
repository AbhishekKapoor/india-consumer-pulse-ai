"""
Apify Scraper — India Consumer Pulse AI

Supports multiple data sources: Reddit, YouTube, Amazon Reviews, Google News.
Falls back to sample CSV data if Apify is not configured or all scrapers fail.

Apify API docs: https://docs.apify.com/api/v2
"""

import hashlib
import json
import logging
import re
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urlencode, quote

import pandas as pd
import requests

from config.settings import settings

logger = logging.getLogger(__name__)

NORMALIZED_COLUMNS = [
    "date", "source", "category", "brand", "topic",
    "url", "author", "text", "engagement", "raw_metadata",
]

# Maps UI source label -> internal source tag
SOURCE_MAP = {
    "Reddit India":     "reddit",
    "YouTube":          "youtube",
    "Amazon Reviews":   "amazon_review",
    "Google News":      "google_news",
}


# ── Public entry point ────────────────────────────────────────

def scrape_data(
    sources: list[str],
    keywords: list[str],
    brands: list[str],
    date_from: str,
    date_to: str,
    category: str,
) -> pd.DataFrame:
    """
    Fetch consumer conversations from one or more sources for the given date range.

    Args:
        sources:   List of UI source labels e.g. ["Reddit India", "YouTube"]
                   Pass ["Sample Data"] to use built-in sample dataset.
        date_from: ISO date string "YYYY-MM-DD" (inclusive)
        date_to:   ISO date string "YYYY-MM-DD" (inclusive)
    """
    if "Sample Data" in sources or not settings.apify_configured:
        if not settings.apify_configured and sources != ["Sample Data"]:
            logger.warning("Apify token not set — loading sample data instead")
        return _load_sample_data(category, keywords, brands, date_from, date_to)

    live_sources = [s for s in sources if s in SOURCE_MAP]
    logger.info(
        f"Scraping {len(live_sources)} source(s) in parallel: {live_sources} | "
        f"{date_from} to {date_to}"
    )

    frames: list[pd.DataFrame] = []

    def _scrape_one(source_label: str) -> tuple[str, Optional[pd.DataFrame]]:
        tag = SOURCE_MAP[source_label]
        try:
            return source_label, _dispatch_scraper(
                tag, keywords, brands, date_from, date_to, category
            )
        except Exception as e:
            logger.error(f"{source_label} scraper raised: {e}")
            return source_label, None

    # Run all sources concurrently — Apify actors (YouTube, Google News) block for
    # minutes each; parallel execution cuts total wait to max(individual times).
    with ThreadPoolExecutor(max_workers=max(1, len(live_sources))) as pool:
        futures = {pool.submit(_scrape_one, src): src for src in live_sources}
        for future in as_completed(futures):
            src, df = future.result()
            if df is not None and not df.empty:
                frames.append(df)
                logger.info(f"  {src}: {len(df)} records")
            else:
                logger.warning(f"  {src}: returned no data")

    if not frames:
        logger.warning("All scrapers returned no data — falling back to sample data")
        return _load_sample_data(category, keywords, brands, date_from, date_to)

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["url", "text"]).reset_index(drop=True)
    logger.info(f"Total combined: {len(combined)} records from {len(frames)} source(s)")
    return combined


def _dispatch_scraper(
    tag: str,
    keywords: list[str],
    brands: list[str],
    date_from: str,
    date_to: str,
    category: str,
) -> Optional[pd.DataFrame]:
    if tag == "reddit":
        return _scrape_reddit(keywords, brands, date_from, date_to, category)
    if tag == "youtube":
        return _scrape_youtube(keywords, brands, date_from, date_to, category)
    if tag == "amazon_review":
        return _scrape_amazon(keywords, brands, date_from, date_to, category)
    if tag == "google_news":
        return _scrape_google_news(keywords, brands, date_from, date_to, category)
    return None


# ── Date-range helpers ────────────────────────────────────────

def _compute_max_records(date_from: str, date_to: str, per_day: int = 30) -> int:
    try:
        d1 = datetime.strptime(date_from, "%Y-%m-%d")
        d2 = datetime.strptime(date_to, "%Y-%m-%d")
        days = max(1, (d2 - d1).days + 1)
        return min(days * per_day + 50, 5000)
    except Exception:
        return 200


def _in_date_range(date_str: str, date_from: str, date_to: str) -> bool:
    return date_from <= date_str <= date_to


# ── Apify API core ────────────────────────────────────────────

def _run_apify_actor(actor_id: str, input_data: dict) -> Optional[list[dict]]:
    token = settings.APIFY_API_TOKEN
    base = "https://api.apify.com/v2"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Apify REST API uses tilde as username/actor separator: trudax~actor-name
    actor_slug = actor_id.replace("/", "~")
    try:
        start = requests.post(
            f"{base}/acts/{actor_slug}/runs",
            headers=headers,
            json=input_data,
            timeout=30,
        )
        start.raise_for_status()
        run_id = start.json()["data"]["id"]
        logger.info(f"Apify run started: {run_id} | actor: {actor_id}")
    except Exception as e:
        logger.error(f"Failed to start Apify actor {actor_slug}: {e}")
        return None

    for _ in range(36):  # poll up to 3 minutes
        time.sleep(5)
        try:
            resp = requests.get(f"{base}/actor-runs/{run_id}", headers=headers, timeout=15)
            status = resp.json()["data"]["status"]
            if status == "SUCCEEDED":
                break
            if status in ("FAILED", "ABORTED", "TIMED-OUT"):
                # Fetch exit message for diagnosis
                exit_msg = resp.json().get("data", {}).get("exitMessage", "no details")
                logger.error(f"Apify run {run_id} ended: {status} — {exit_msg}")
                return None
        except Exception as e:
            logger.warning(f"Poll error run {run_id}: {e}")

    try:
        items_resp = requests.get(
            f"{base}/actor-runs/{run_id}/dataset/items",
            headers=headers,
            params={"format": "json"},
            timeout=60,
        )
        items_resp.raise_for_status()
        items = items_resp.json()
        logger.info(f"Apify returned {len(items)} raw items")
        return items
    except Exception as e:
        logger.error(f"Failed to fetch dataset for run {run_id}: {e}")
        return None


# ── Reddit ────────────────────────────────────────────────────

_INDIA_SUBREDDITS = [
    "india", "suggestalaptop", "indiangaming", "laptops",
    "oneplus", "samsung", "hardware", "IndiaInvestments",
]

# Subreddits whose entire audience is Indian — posts from these don't need
# an explicit India mention to be considered in-scope.
_INDIA_NATIVE_SUBREDDITS: frozenset[str] = frozenset({
    "india", "indiangaming", "GadgetsIndia", "IndiaInvestments",
    "techIndia", "indiasocial", "bangalore", "delhi", "mumbai",
    "pune", "hyderabad", "chennai", "kolkata",
})

# Signals that strongly indicate the post is written from / for an Indian context.
# Checked (case-insensitive) against post text for posts from global subreddits.
_INDIA_SIGNALS: frozenset[str] = frozenset({
    # Country / nationality
    "india", "indian", "bharat",
    # Currency
    "₹", " inr", "rs.", "lakh", "crore", "rupee", "rupees",
    # Indian cities
    "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai",
    "kolkata", "pune", "ahmedabad", "noida", "gurgaon", "gurugram",
    "jaipur", "lucknow", "chandigarh", "kochi", "indore", "surat",
    # E-commerce / retail
    "flipkart", "croma", "reliance digital", "vijay sales", "tata cliq",
    # Telecom
    "jio", "airtel", "bsnl",
    # Payments
    "upi", "paytm", "phonepe", "gpay", "google pay",
    # Tax / duty
    "gst", "import duty", "customs duty",
})


def _is_india_context(text: str, subreddit: str) -> bool:
    """
    Returns True if the post is verifiably from/for an Indian audience.
    Posts from India-native subreddits are trusted implicitly.
    Posts from global subreddits (r/suggestalaptop, r/laptops, etc.) must
    contain at least one explicit India signal in the text.
    """
    if subreddit in _INDIA_NATIVE_SUBREDDITS:
        return True
    text_lower = text.lower()
    return any(signal in text_lower for signal in _INDIA_SIGNALS)


_PULLPUSH_BASE = "https://api.pullpush.io/reddit/search/submission/"

# Reddit native API — no auth needed, rate limit ~1 req/sec unauthenticated
_REDDIT_HEADERS = {"User-Agent": "IndiaConsumerPulseAI/1.0 (research, non-commercial)"}

# Combined subreddit cluster for keyword search (searches all at once)
_INDIA_SUB_CLUSTER = (
    "india+suggestalaptop+indiangaming+laptops+GadgetsIndia+"
    "techIndia+oneplus+samsung+hardware+apple+lenovo"
)

# Subreddits where we browse the full 'new' listing.
# r/india is intentionally excluded here — it's a general subreddit and produces
# too many off-topic posts when browsed without a keyword constraint.
# It IS still included in _INDIA_SUB_CLUSTER for keyword-filtered search.
_FOCUSED_SUBS = ["suggestalaptop", "indiangaming", "GadgetsIndia", "laptops"]


def _days_to_reddit_filter(days: int) -> str:
    if days <= 1:   return "day"
    if days <= 7:   return "week"
    if days <= 31:  return "month"
    if days <= 365: return "year"
    return "all"


def _scrape_reddit(
    keywords: list[str], brands: list[str],
    date_from: str, date_to: str, category: str,
) -> Optional[pd.DataFrame]:
    try:
        d1 = datetime.strptime(date_from, "%Y-%m-%d")
        d2 = datetime.strptime(date_to, "%Y-%m-%d")
        days = (d2 - d1).days
    except Exception:
        days = 7

    # When running with an Apify token (e.g. on cloud hosting where Reddit blocks datacenter IPs),
    # use the Apify actor first — it routes through residential proxies that Reddit accepts.
    if settings.apify_configured:
        logger.info(f"Reddit: Apify token present — trying actor first (avoids cloud IP blocks)")
        df = _scrape_reddit_via_apify(keywords, brands, date_from, date_to, category)
        if df is not None and not df.empty:
            logger.info(f"Reddit: Apify actor returned {len(df)} records")
            return df
        logger.info("Reddit: Apify actor returned no data — falling back to native API")

    logger.info(f"Reddit: {days}-day range — using native JSON API")
    df = _scrape_reddit_native(keywords, brands, date_from, date_to, category, days)

    # Supplement with PullPush comments if native returned data and range is ≥ 3 days
    if df is not None and not df.empty and days >= 3:
        comment_df = _scrape_pullpush_comments_only(keywords, brands, date_from, date_to, category)
        if comment_df is not None and not comment_df.empty:
            df = pd.concat([df, comment_df], ignore_index=True)
            df = df.drop_duplicates(subset=["url", "text"]).reset_index(drop=True)
            logger.info(f"Reddit total after PullPush comment supplement: {len(df)} records")

    return df


def _scrape_reddit_native(
    keywords: list[str], brands: list[str],
    date_from: str, date_to: str, category: str,
    days: int,
) -> Optional[pd.DataFrame]:
    """
    Reddit native JSON API — completely free, no API key or Apify needed.
    Two strategies combined:
      1. Keyword search across the Indian subreddit cluster (relevant posts)
      2. Full new-listing browse for focused subreddits (comprehensive coverage)
    """
    d1 = datetime.strptime(date_from, "%Y-%m-%d")
    d2 = datetime.strptime(date_to, "%Y-%m-%d")
    after_ts  = int(d1.timestamp())
    before_ts = int(d2.timestamp()) + 86400
    time_filter = _days_to_reddit_filter(days)

    seen_ids: set[str] = set()
    raw_posts: list[dict] = []

    # Strategy 1: keyword search across the full Indian subreddit cluster
    for kw in keywords[:8]:
        fetched = _reddit_search_pages(kw, _INDIA_SUB_CLUSTER, time_filter, seen_ids, after_ts, before_ts)
        raw_posts.extend(fetched)
        logger.debug(f"Reddit native search [{kw}]: {len(fetched)} posts")
        time.sleep(1.5)

    # Strategy 2: browse new-listing of focused subreddits (catches posts not found by keyword search)
    for sub in _FOCUSED_SUBS:
        fetched = _reddit_new_listing(sub, seen_ids, after_ts, before_ts)
        raw_posts.extend(fetched)
        logger.debug(f"Reddit native new [r/{sub}]: {len(fetched)} posts")
        time.sleep(1.5)

    logger.info(f"Reddit native API: {len(raw_posts)} raw posts collected")

    rows = []
    skipped_irrelevant = 0
    skipped_non_india = 0
    for post in raw_posts:
        title = post.get("title", "")
        body  = post.get("selftext", "")
        text  = f"{title} {body}".strip()
        if len(text) < 30 or body in ("[deleted]", "[removed]"):
            continue
        if not _is_relevant(text, keywords, brands):
            skipped_irrelevant += 1
            continue
        subreddit = post.get("subreddit", "")
        if not _is_india_context(text, subreddit):
            skipped_non_india += 1
            continue
        ts       = post.get("created_utc", 0)
        date_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        author_hash = hashlib.md5(post.get("author", "anon").encode()).hexdigest()[:10]
        rows.append({
            "date":         date_str,
            "source":       "reddit",
            "category":     category,
            "brand":        _detect_brand(text, brands),
            "topic":        title[:120],
            "url":          f"https://reddit.com{post.get('permalink', '')}",
            "author":       f"user_{author_hash}",
            "text":         text[:1500],
            "engagement":   post.get("score", 0),
            "raw_metadata": json.dumps({
                "subreddit":    subreddit,
                "num_comments": post.get("num_comments", 0),
                "type":         "post",
            }),
        })

    logger.info(
        f"Reddit native API: {len(rows)} rows kept "
        f"({skipped_irrelevant} off-topic, {skipped_non_india} non-India dropped)"
    )
    if not rows:
        logger.warning("Reddit native API returned 0 rows — falling back to PullPush historical")
        return _scrape_reddit_historical(keywords, brands, date_from, date_to, category)
    return pd.DataFrame(rows, columns=NORMALIZED_COLUMNS)


def _reddit_search_pages(
    keyword: str,
    sub_cluster: str,
    time_filter: str,
    seen_ids: set,
    after_ts: int,
    before_ts: int,
    max_pages: int = 3,
) -> list[dict]:
    """
    Search Reddit for a keyword across a subreddit cluster.
    Paginates using Reddit's 'after' fullname cursor (up to max_pages × 100 = 300 posts).
    """
    results: list[dict] = []
    after_fullname: Optional[str] = None

    for _ in range(max_pages):
        params: dict = {
            "q": keyword, "sort": "new", "t": time_filter,
            "limit": 100, "restrict_sr": "on",
        }
        if after_fullname:
            params["after"] = after_fullname

        try:
            resp = requests.get(
                f"https://www.reddit.com/r/{sub_cluster}/search.json",
                params=params, headers=_REDDIT_HEADERS, timeout=20,
            )
            if resp.status_code == 429:
                logger.debug("Reddit rate limited — backing off 10s")
                time.sleep(10)
                continue
            resp.raise_for_status()
            data = resp.json().get("data", {})
        except Exception as e:
            logger.debug(f"Reddit search [{keyword}] error: {e}")
            break

        children = data.get("children", [])
        if not children:
            break

        for child in children:
            post = child.get("data", {})
            pid  = post.get("id")
            if not pid or pid in seen_ids:
                continue
            created = post.get("created_utc", 0)
            if not (after_ts <= created <= before_ts):
                continue
            seen_ids.add(pid)
            results.append(post)

        after_fullname = data.get("after")
        if not after_fullname:
            break
        time.sleep(1.5)

    return results


def _reddit_new_listing(
    subreddit: str,
    seen_ids: set,
    after_ts: int,
    before_ts: int,
    max_pages: int = 5,
) -> list[dict]:
    """
    Browse a subreddit's 'new' listing and collect all posts within [after_ts, before_ts].
    Paginates backwards in time using 'after' fullname cursor until we pass after_ts.
    """
    results: list[dict] = []
    after_fullname: Optional[str] = None

    for _ in range(max_pages):
        params: dict = {"limit": 100}
        if after_fullname:
            params["after"] = after_fullname

        try:
            resp = requests.get(
                f"https://www.reddit.com/r/{subreddit}/new.json",
                params=params, headers=_REDDIT_HEADERS, timeout=20,
            )
            if resp.status_code == 429:
                time.sleep(10)
                continue
            resp.raise_for_status()
            data = resp.json().get("data", {})
        except Exception as e:
            logger.debug(f"Reddit new [r/{subreddit}] error: {e}")
            break

        children = data.get("children", [])
        if not children:
            break

        last_fullname: Optional[str] = None
        hit_before_window = False

        for child in children:
            post    = child.get("data", {})
            pid     = post.get("id")
            created = post.get("created_utc", 0)
            if not pid:
                continue
            if created < after_ts:
                hit_before_window = True
                break
            if created <= before_ts and pid not in seen_ids:
                seen_ids.add(pid)
                results.append(post)
            last_fullname = child.get("kind", "t3") + "_" + pid

        if hit_before_window or not last_fullname:
            break
        after_fullname = last_fullname
        time.sleep(1.5)

    return results


_PULLPUSH_COMMENT_BASE = "https://api.pullpush.io/reddit/search/comment/"

_EXTENDED_INDIA_SUBREDDITS = [
    "india", "suggestalaptop", "indiangaming", "laptops",
    "oneplus", "samsung", "hardware", "IndiaInvestments",
    "GadgetsIndia", "techIndia", "apple", "lenovo",
]


def _pullpush_paginated(
    base_url: str,
    params: dict,
    seen_ids: set,
    max_per_query: int = 300,
) -> list[dict]:
    """
    Fetch up to max_per_query items from PullPush using cursor-based pagination.
    Each page returns up to 100 items; pages by moving 'before' to oldest timestamp.
    """
    collected: list[dict] = []
    before_ts = params["before"]

    for page in range(max_per_query // 100):
        page_params = {**params, "before": before_ts}
        try:
            resp = requests.get(base_url, params=page_params, timeout=30)
            resp.raise_for_status()
            batch = resp.json().get("data", [])
        except Exception as e:
            logger.debug(f"PullPush page {page + 1} failed: {e}")
            break

        if not batch:
            break

        added = 0
        for item in batch:
            pid = item.get("id")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                collected.append(item)
                added += 1

        # Advance cursor to just before the oldest post in this batch
        oldest_ts = min(item.get("created_utc", before_ts) for item in batch)
        if oldest_ts >= before_ts or len(batch) < 100:
            break   # no more pages
        before_ts = oldest_ts - 1
        time.sleep(0.8)

    return collected


def _scrape_pullpush_comments_only(
    keywords: list[str], brands: list[str],
    date_from: str, date_to: str, category: str,
) -> Optional[pd.DataFrame]:
    """
    Fetch Reddit comments via PullPush.io to supplement native-API post data.
    Comments aren't available from the native API without OAuth, so PullPush
    is used as a bonus layer when it's available.
    """
    d1 = datetime.strptime(date_from, "%Y-%m-%d")
    d2 = datetime.strptime(date_to, "%Y-%m-%d")
    after_ts  = int(d1.timestamp())
    before_ts = int(d2.timestamp()) + 86400
    base_params = {"after": after_ts, "before": before_ts, "size": 100}

    all_comments: list[dict] = []
    seen_ids: set[str] = set()

    for kw in keywords[:6]:
        fetched = _pullpush_paginated(
            _PULLPUSH_COMMENT_BASE, {**base_params, "q": kw}, seen_ids, max_per_query=200
        )
        all_comments.extend(fetched)
        logger.debug(f"PullPush comments [{kw}]: {len(fetched)}")
        time.sleep(0.5)

    for sub in _EXTENDED_INDIA_SUBREDDITS[:4]:
        fetched = _pullpush_paginated(
            _PULLPUSH_COMMENT_BASE,
            {**base_params, "subreddit": sub, "q": " OR ".join(keywords[:4])},
            seen_ids, max_per_query=200,
        )
        all_comments.extend(fetched)
        logger.debug(f"PullPush comments [r/{sub}]: {len(fetched)}")
        time.sleep(0.5)

    logger.info(f"PullPush comments: {len(all_comments)} raw before filtering")
    rows = []
    skipped_irrelevant = 0
    skipped_non_india = 0
    for item in all_comments:
        text = item.get("body", "").strip()
        if len(text) < 30 or text in ("[deleted]", "[removed]"):
            continue
        ts       = item.get("created_utc", 0)
        date_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        if not _in_date_range(date_str, date_from, date_to):
            continue
        if not _is_relevant(text, keywords, brands):
            skipped_irrelevant += 1
            continue
        subreddit = item.get("subreddit", "")
        if not _is_india_context(text, subreddit):
            skipped_non_india += 1
            continue
        author_hash = hashlib.md5(item.get("author", "anon").encode()).hexdigest()[:10]
        rows.append({
            "date":         date_str,
            "source":       "reddit",
            "category":     category,
            "brand":        _detect_brand(text, brands),
            "topic":        item.get("link_title", text[:80]),
            "url":          f"https://reddit.com{item.get('permalink', '')}",
            "author":       f"user_{author_hash}",
            "text":         text[:1500],
            "engagement":   item.get("score", 0),
            "raw_metadata": json.dumps({"subreddit": subreddit, "type": "comment"}),
        })
    logger.info(
        f"PullPush comments: {len(rows)} rows kept "
        f"({skipped_irrelevant} off-topic, {skipped_non_india} non-India dropped)"
    )
    return pd.DataFrame(rows, columns=NORMALIZED_COLUMNS) if rows else None


def _scrape_reddit_historical(
    keywords: list[str], brands: list[str],
    date_from: str, date_to: str, category: str,
) -> Optional[pd.DataFrame]:
    """
    Fetch Reddit posts + comments via PullPush.io.
    Used as fallback when the native Reddit API returns nothing.
    """
    d1 = datetime.strptime(date_from, "%Y-%m-%d")
    d2 = datetime.strptime(date_to, "%Y-%m-%d")
    after_ts  = int(d1.timestamp())
    before_ts = int(d2.timestamp()) + 86400

    all_posts:    list[dict] = []
    all_comments: list[dict] = []
    seen_ids: set[str] = set()

    # sort_type=created_utc (default, newest first) is required for cursor-based pagination.
    # sort=score would return top-100 across the whole range on page 1, killing further pages.
    base_params = {"after": after_ts, "before": before_ts, "size": 100, "sort_type": "created_utc", "sort": "desc"}

    # ── Posts: per keyword (paginated) ───────────────────────
    for kw in keywords[:8]:
        fetched = _pullpush_paginated(
            _PULLPUSH_BASE, {**base_params, "q": kw}, seen_ids, max_per_query=300
        )
        all_posts.extend(fetched)
        logger.debug(f"PullPush posts [{kw}]: {len(fetched)}")
        time.sleep(0.5)

    # ── Posts: per Indian subreddit (paginated) ───────────────
    for sub in _EXTENDED_INDIA_SUBREDDITS[:6]:
        fetched = _pullpush_paginated(
            _PULLPUSH_BASE,
            {**base_params, "subreddit": sub, "q": " OR ".join(keywords[:5])},
            seen_ids,
            max_per_query=200,
        )
        all_posts.extend(fetched)
        logger.debug(f"PullPush posts [r/{sub}]: {len(fetched)}")
        time.sleep(0.5)

    # ── Comments: per keyword (higher volume than posts) ──────
    for kw in keywords[:6]:
        fetched = _pullpush_paginated(
            _PULLPUSH_COMMENT_BASE, {**base_params, "q": kw}, seen_ids, max_per_query=200
        )
        all_comments.extend(fetched)
        logger.debug(f"PullPush comments [{kw}]: {len(fetched)}")
        time.sleep(0.5)

    # ── Comments: key Indian subreddits ──────────────────────
    for sub in _EXTENDED_INDIA_SUBREDDITS[:4]:
        fetched = _pullpush_paginated(
            _PULLPUSH_COMMENT_BASE,
            {**base_params, "subreddit": sub, "q": " OR ".join(keywords[:4])},
            seen_ids,
            max_per_query=200,
        )
        all_comments.extend(fetched)
        logger.debug(f"PullPush comments [r/{sub}]: {len(fetched)}")
        time.sleep(0.5)

    logger.info(
        f"PullPush: {len(all_posts)} posts + {len(all_comments)} comments "
        f"= {len(all_posts) + len(all_comments)} total before filtering"
    )

    rows = []
    skipped_irrelevant = 0
    skipped_non_india = 0

    # Build rows from posts
    for item in all_posts:
        title = item.get("title", "")
        body  = item.get("selftext", "")
        text  = f"{title} {body}".strip()
        if len(text) < 30 or text in ("[deleted]", "[removed]"):
            continue
        ts       = item.get("created_utc", 0)
        date_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        if not _in_date_range(date_str, date_from, date_to):
            continue
        if not _is_relevant(text, keywords, brands):
            skipped_irrelevant += 1
            continue
        subreddit = item.get("subreddit", "")
        if not _is_india_context(text, subreddit):
            skipped_non_india += 1
            continue
        author_hash = hashlib.md5(item.get("author", "anon").encode()).hexdigest()[:10]
        rows.append({
            "date":         date_str,
            "source":       "reddit",
            "category":     category,
            "brand":        _detect_brand(text, brands),
            "topic":        title[:120],
            "url":          f"https://reddit.com{item.get('permalink', '')}",
            "author":       f"user_{author_hash}",
            "text":         text[:1500],
            "engagement":   item.get("score", 0),
            "raw_metadata": json.dumps({
                "subreddit":    subreddit,
                "num_comments": item.get("num_comments", 0),
                "type":         "post",
            }),
        })

    # Build rows from comments
    for item in all_comments:
        text = item.get("body", "").strip()
        if len(text) < 30 or text in ("[deleted]", "[removed]"):
            continue
        ts       = item.get("created_utc", 0)
        date_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        if not _in_date_range(date_str, date_from, date_to):
            continue
        if not _is_relevant(text, keywords, brands):
            skipped_irrelevant += 1
            continue
        subreddit = item.get("subreddit", "")
        if not _is_india_context(text, subreddit):
            skipped_non_india += 1
            continue
        author_hash = hashlib.md5(item.get("author", "anon").encode()).hexdigest()[:10]
        rows.append({
            "date":         date_str,
            "source":       "reddit",
            "category":     category,
            "brand":        _detect_brand(text, brands),
            "topic":        item.get("link_title", text[:80]),
            "url":          f"https://reddit.com{item.get('permalink', '')}",
            "author":       f"user_{author_hash}",
            "text":         text[:1500],
            "engagement":   item.get("score", 0),
            "raw_metadata": json.dumps({
                "subreddit": subreddit,
                "type":      "comment",
            }),
        })

    logger.info(
        f"PullPush Reddit: {len(rows)} rows kept "
        f"({skipped_irrelevant} off-topic, {skipped_non_india} non-India dropped)"
    )
    if not rows:
        logger.warning("PullPush returned no data — falling back to Apify actor")
        return _scrape_reddit_via_apify(keywords, brands, date_from, date_to, category)
    return pd.DataFrame(rows, columns=NORMALIZED_COLUMNS)


def _scrape_reddit_via_apify(
    keywords: list[str], brands: list[str],
    date_from: str, date_to: str, category: str,
) -> Optional[pd.DataFrame]:
    """
    Apify Reddit scrape using trudax/reddit-scraper-lite.
    Input schema: startUrls array of Reddit search page URLs.
    Works from cloud hosting via Apify's residential proxies.
    """
    try:
        d1 = datetime.strptime(date_from, "%Y-%m-%d")
        d2 = datetime.strptime(date_to, "%Y-%m-%d")
        days = max(1, (d2 - d1).days)
    except Exception:
        days = 7
    time_filter = _days_to_reddit_filter(days)

    # Build Reddit search URLs — keywords × subreddit cluster + focused per-sub searches
    start_urls: list[dict] = []
    for kw in keywords[:8]:
        kw_enc = quote(kw)
        start_urls.append({
            "url": f"https://www.reddit.com/r/{_INDIA_SUB_CLUSTER}/search/?q={kw_enc}&sort=new&t={time_filter}&restrict_sr=on"
        })
    # Brand-specific searches in India subreddits
    for brand in brands[:4]:
        brand_enc = quote(f"{brand} India")
        start_urls.append({
            "url": f"https://www.reddit.com/r/{_INDIA_SUB_CLUSTER}/search/?q={brand_enc}&sort=new&t={time_filter}&restrict_sr=on"
        })
    # Focused subreddits by combined keywords
    for sub in _FOCUSED_SUBS[:4]:
        kw_enc = quote(" OR ".join(keywords[:4]))
        start_urls.append({
            "url": f"https://www.reddit.com/r/{sub}/search/?q={kw_enc}&sort=new&t={time_filter}&restrict_sr=on"
        })

    # Scale maxItems to date range: ~20 items/day target, minimum 300, maximum 800
    max_items = min(max(300, days * 20), 800)
    actor_input = {"startUrls": start_urls, "maxItems": max_items}
    logger.info(f"Apify Reddit: {len(start_urls)} search URLs, t={time_filter}, maxItems={max_items}")

    items = _run_apify_actor(settings.APIFY_REDDIT_ACTOR, actor_input)
    if not items:
        return None

    rows, skipped_date, skipped_india, skipped_short = [], 0, 0, 0
    for item in items:
        title = item.get("title", "")
        body  = item.get("body", "")
        text  = f"{title} {body}".strip()
        if len(text) < 30:
            skipped_short += 1
            continue

        raw_date = item.get("createdAt", item.get("scrapedAt", ""))
        try:
            date_str = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            date_str = datetime.now().strftime("%Y-%m-%d")
        if not _in_date_range(date_str, date_from, date_to):
            skipped_date += 1
            continue

        subreddit = item.get("parsedCommunityName", item.get("communityName", "")).lstrip("r/")
        if not _is_india_context(text, subreddit):
            skipped_india += 1
            continue

        author = item.get("username", item.get("userId", "anon"))
        author_hash = hashlib.md5(str(author).encode()).hexdigest()[:10]
        rows.append({
            "date":         date_str,
            "source":       "reddit",
            "category":     category,
            "brand":        _detect_brand(text, brands),
            "topic":        title[:120],
            "url":          item.get("url", ""),
            "author":       f"user_{author_hash}",
            "text":         text[:1500],
            "engagement":   item.get("upVotes", item.get("score", 0)),
            "raw_metadata": json.dumps({
                "subreddit":    subreddit,
                "num_comments": item.get("numberOfComments", 0),
                "upvote_ratio": item.get("upVoteRatio", 0),
            }),
        })

    logger.info(
        f"Apify Reddit: {len(rows)} kept "
        f"({skipped_date} outside date, {skipped_india} non-India, {skipped_short} too short)"
    )
    return pd.DataFrame(rows, columns=NORMALIZED_COLUMNS) if rows else None


# ── YouTube ───────────────────────────────────────────────────

_YT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _parse_yt_relative_date(time_str: str, date_from: str, date_to: str) -> Optional[str]:
    """Convert YouTube relative timestamps ('3 days ago') to YYYY-MM-DD, filtered to range."""
    if not time_str:
        return date_to
    t = time_str.lower().strip()
    now = datetime.now()
    try:
        n = int(re.search(r"\d+", t).group()) if re.search(r"\d+", t) else 1
        if "hour" in t or "minute" in t or "second" in t:
            d = now
        elif "day" in t:
            d = now - timedelta(days=n)
        elif "week" in t:
            d = now - timedelta(weeks=n)
        elif "month" in t:
            d = now - timedelta(days=n * 30)
        elif "year" in t:
            d = now - timedelta(days=n * 365)
        else:
            d = now
        date_str = d.strftime("%Y-%m-%d")
        return date_str if _in_date_range(date_str, date_from, date_to) else None
    except Exception:
        return date_to


def _extract_yt_initial_data(html: str) -> Optional[dict]:
    """Extract ytInitialData JSON from a YouTube page using raw_decode (no regex truncation)."""
    marker = "ytInitialData = "
    idx = html.find(marker)
    if idx == -1:
        return None
    try:
        data, _ = json.JSONDecoder().raw_decode(html, idx + len(marker))
        return data
    except Exception:
        return None


def _scrape_youtube(
    keywords: list[str], brands: list[str],
    date_from: str, date_to: str, category: str,
) -> Optional[pd.DataFrame]:
    """
    Native YouTube scraper — parses ytInitialData from the search results page.
    No Apify actor or API key required. Falls back to Apify if native returns nothing.
    """
    year = datetime.now().year
    search_queries: list[str] = []
    for brand in brands[:4]:
        search_queries.append(f"{brand} India review {year}")
    for kw in keywords[:3]:
        search_queries.append(f"{kw} India")

    rows: list[dict] = []
    seen_ids: set[str] = set()
    skipped_date = 0
    skipped_india = 0

    for query in search_queries[:6]:
        url = f"https://www.youtube.com/results?search_query={quote(query)}&sp=CAI%3D"
        try:
            resp = requests.get(url, headers=_YT_HEADERS, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            logger.debug(f"YouTube native [{query}]: {e}")
            time.sleep(1.0)
            continue

        data = _extract_yt_initial_data(resp.text)
        if not data:
            logger.debug(f"YouTube native [{query}]: ytInitialData not found")
            time.sleep(1.0)
            continue

        # Navigate to video results — structure:
        # contents → twoColumnSearchResultsRenderer → primaryContents →
        # sectionListRenderer → contents[] → itemSectionRenderer → contents[]
        try:
            sections = (
                data["contents"]["twoColumnSearchResultsRenderer"]
                    ["primaryContents"]["sectionListRenderer"]["contents"]
            )
        except (KeyError, TypeError):
            logger.debug(f"YouTube native [{query}]: unexpected page structure")
            time.sleep(1.0)
            continue

        for section in sections:
            for item in section.get("itemSectionRenderer", {}).get("contents", []):
                vid = item.get("videoRenderer", {})
                if not vid:
                    continue

                video_id = vid.get("videoId", "")
                if not video_id or video_id in seen_ids:
                    continue
                seen_ids.add(video_id)

                # Title
                try:
                    title = vid["title"]["runs"][0]["text"]
                except (KeyError, IndexError):
                    title = ""

                # Description snippet
                try:
                    desc = " ".join(
                        r.get("text", "")
                        for r in vid.get("descriptionSnippet", {}).get("runs", [])
                    )
                except Exception:
                    desc = ""

                text = f"{title} {desc}".strip()
                if len(text) < 30:
                    continue

                # Channel
                try:
                    channel = (
                        vid.get("longBylineText", {}).get("runs", [{}])[0].get("text", "") or
                        vid.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
                    )
                except Exception:
                    channel = ""

                # View count
                try:
                    view_str = (
                        vid.get("viewCountText", {}).get("simpleText", "") or
                        vid.get("viewCountText", {}).get("runs", [{}])[0].get("text", "0")
                    )
                    views = int("".join(c for c in view_str if c.isdigit()) or "0")
                except Exception:
                    views = 0

                # Date — YouTube gives relative time, convert to absolute
                pub_time = vid.get("publishedTimeText", {}).get("simpleText", "")
                date_str = _parse_yt_relative_date(pub_time, date_from, date_to)
                if date_str is None:
                    skipped_date += 1
                    continue

                # India context — search queries include "India" so title already signals it
                combined = f"India {text}"
                if not _is_india_context(combined, ""):
                    skipped_india += 1
                    continue

                author_hash = hashlib.md5(channel.encode()).hexdigest()[:10]
                rows.append({
                    "date":         date_str,
                    "source":       "youtube",
                    "category":     category,
                    "brand":        _detect_brand(combined, brands),
                    "topic":        title[:120],
                    "url":          f"https://www.youtube.com/watch?v={video_id}",
                    "author":       f"user_{author_hash}",
                    "text":         text[:1500],
                    "engagement":   views,
                    "raw_metadata": json.dumps({
                        "video_id":      video_id,
                        "channel":       channel,
                        "published_time": pub_time,
                    }),
                })

        time.sleep(1.2)

    logger.info(
        f"YouTube native: {len(rows)} videos kept "
        f"({skipped_date} outside date range, {skipped_india} non-India dropped)"
    )

    if rows:
        return pd.DataFrame(rows, columns=NORMALIZED_COLUMNS)

    # Apify fallback — only reached if native returns nothing
    logger.info("YouTube native returned 0 rows — attempting Apify fallback")
    actor_input = {
        "searchKeywords": "\n".join(search_queries[:6]),
        "maxResults": 20,
        "downloadComments": False,
    }
    items = _run_apify_actor(settings.APIFY_YOUTUBE_ACTOR, actor_input)
    if not items:
        return None

    apify_rows = []
    for item in items:
        text = item.get("text", item.get("description", ""))
        if len(str(text)) < 30:
            continue
        raw_date = item.get("date", item.get("publishedAt", ""))
        try:
            date_str = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            date_str = datetime.now().strftime("%Y-%m-%d")
        if not _in_date_range(date_str, date_from, date_to):
            continue
        title = item.get("title", "")
        channel = item.get("channelName", item.get("author", ""))
        author_hash = hashlib.md5(str(channel).encode()).hexdigest()[:10]
        apify_rows.append({
            "date": date_str, "source": "youtube", "category": category,
            "brand": _detect_brand(f"India {title} {text}", brands),
            "topic": title[:120],
            "url": item.get("url", ""),
            "author": f"user_{author_hash}",
            "text": str(text)[:1500],
            "engagement": item.get("likes", item.get("viewCount", 0)),
            "raw_metadata": json.dumps({"video_title": title[:100], "channel": channel}),
        })

    logger.info(f"YouTube Apify fallback: {len(apify_rows)} rows")
    return pd.DataFrame(apify_rows, columns=NORMALIZED_COLUMNS) if apify_rows else None


# ── Amazon Reviews ────────────────────────────────────────────

def _scrape_amazon(
    keywords: list[str], brands: list[str],
    date_from: str, date_to: str, category: str,
) -> Optional[pd.DataFrame]:
    from scrapers.amazon_asin_cache import get_product_urls

    product_urls = get_product_urls(brands, category)

    if not product_urls:
        logger.warning("Amazon: ASIN discovery returned no products — skipping this source.")
        return None

    # Scale pages per product to the date window (10 reviews/page, capped at 3 for cost control)
    try:
        _days = max(1, (datetime.strptime(date_to, "%Y-%m-%d") -
                        datetime.strptime(date_from, "%Y-%m-%d")).days + 1)
    except Exception:
        _days = 30
    reviews_per_product = min(max(20, _days * 2), 200)
    max_pages = min(max(1, reviews_per_product // 10), 3)

    # Extract ASINs from cached URLs (format: https://www.amazon.in/dp/{ASIN})
    _ASIN_RE = re.compile(r"/dp/([A-Z0-9]{10})")
    asins: list[str] = []
    for url in product_urls[:20]:
        m = _ASIN_RE.search(url)
        if m:
            asins.append(m.group(1))

    if not asins:
        logger.warning("Amazon: no valid ASINs extracted from product URLs — skipping.")
        return None

    # axesso_data/amazon-reviews-scraper input schema:
    # input array with one entry per ASIN: {asin, domainCode, sortBy, maxPages}
    actor_input = {
        "input": [
            {"asin": asin, "domainCode": "in", "sortBy": "recent", "maxPages": max_pages}
            for asin in asins
        ]
    }
    logger.info(
        f"Amazon: scraping {len(asins)} ASINs, "
        f"{max_pages} pages/product (~{max_pages * 10} reviews each, {_days}-day window)"
    )
    items = _run_apify_actor(settings.APIFY_AMAZON_ACTOR, actor_input)
    if not items:
        return None

    rows, skipped = [], 0
    for item in items:
        # axesso output: reviewText + reviewTitle (same as original field names)
        review_text  = item.get("reviewText", item.get("body", item.get("text", "")))
        review_title = item.get("reviewTitle", item.get("title", ""))
        combined     = f"{review_title} {review_text}".strip()
        if len(combined) < 30:
            continue

        raw_date = item.get("reviewDate", item.get("date", item.get("scrapedAt", "")))
        try:
            date_str = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # Amazon reviews are evergreen — a bad service experience from 6 months ago
        # is still a valid brand signal. Include all fetched reviews but keep the date
        # so the AI can weigh recency in its analysis.

        product     = item.get("productTitle", item.get("product", ""))
        reviewer    = item.get("reviewerName", item.get("reviewer", item.get("reviewId", "anon")))
        author_hash = hashlib.md5(str(reviewer).encode()).hexdigest()[:10]
        rating      = item.get("rating", item.get("ratingText", 0))
        try:
            rating = float(str(rating).split("/")[0].strip())
        except Exception:
            rating = 0

        rows.append({
            "date":         date_str,
            "source":       "amazon_review",
            "category":     category,
            "brand":        _detect_brand(f"{product} {combined}", brands),
            "topic":        review_title[:120] or product[:120],
            "url":          item.get("reviewUrl", item.get("url", item.get("productUrl", ""))),
            "author":       f"user_{author_hash}",
            "text":         combined[:1500],
            "engagement":   item.get("helpfulVotes", item.get("helpful", 0)),
            "raw_metadata": json.dumps({
                "product":       product[:100],
                "asin":          item.get("productAsin", item.get("asin", "")),
                "rating":        rating,
                "verified":      item.get("verifiedPurchase", item.get("verified", True)),
                "total_reviews": item.get("totalReviews", 0),
            }),
        })

    logger.info(f"Amazon: {len(rows)} kept, {skipped} outside date range")
    return pd.DataFrame(rows, columns=NORMALIZED_COLUMNS) if rows else None


# ── Google News ───────────────────────────────────────────────

_GN_RSS_BASE = "https://news.google.com/rss/search"
_GN_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IndiaConsumerPulseAI/1.0)"}


def _scrape_google_news(
    keywords: list[str], brands: list[str],
    date_from: str, date_to: str, category: str,
) -> Optional[pd.DataFrame]:
    """
    Google News via public RSS feed — free, no API key, no Apify actor required.
    Uses India-specific locale parameters (hl=en-IN, gl=IN).
    """
    search_terms = [f"{kw} India" for kw in keywords[:6]]
    for brand in brands[:3]:
        search_terms.append(f"{brand} India")

    rows: list[dict] = []
    seen_urls: set[str] = set()
    skipped = 0

    for query in search_terms[:8]:
        params = {"q": query, "hl": "en-IN", "gl": "IN", "ceid": "IN:en"}
        url = f"{_GN_RSS_BASE}?{urlencode(params)}"
        try:
            resp = requests.get(url, headers=_GN_HEADERS, timeout=15)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except Exception as e:
            logger.debug(f"Google News RSS [{query}] fetch error: {e}")
            time.sleep(0.5)
            continue

        channel = root.find("channel")
        if channel is None:
            continue

        for item in channel.findall("item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "")
            description = item.findtext("description", "").strip()
            source_elem = item.find("source")
            publisher = source_elem.text if source_elem is not None else ""

            combined = f"{title} {description}".strip()
            if len(combined) < 30 or not link or link in seen_urls:
                continue
            seen_urls.add(link)

            try:
                date_str = parsedate_to_datetime(pub_date).strftime("%Y-%m-%d")
            except Exception:
                date_str = datetime.now().strftime("%Y-%m-%d")

            if not _in_date_range(date_str, date_from, date_to):
                skipped += 1
                continue

            rows.append({
                "date":         date_str,
                "source":       "google_news",
                "category":     category,
                "brand":        _detect_brand(combined, brands),
                "topic":        title[:120],
                "url":          link,
                "author":       f"user_gn_{hashlib.md5(publisher.encode()).hexdigest()[:8]}",
                "text":         combined[:1500],
                "engagement":   0,
                "raw_metadata": json.dumps({
                    "publication": publisher,
                    "headline":    title[:150],
                }),
            })

        time.sleep(0.5)

    logger.info(f"Google News RSS: {len(rows)} kept, {skipped} outside date range")
    return pd.DataFrame(rows, columns=NORMALIZED_COLUMNS) if rows else None


# ── Brand detection ───────────────────────────────────────────

# Product-name aliases → canonical brand name.
# Checked after the direct brand-name scan so explicit matches still win.
_BRAND_ALIASES: dict[str, str] = {
    # Apple
    "macbook": "Apple", "macbook air": "Apple", "macbook pro": "Apple",
    "imac": "Apple", "mac mini": "Apple", "iphone": "Apple", "ipad": "Apple",
    "airpods": "Apple", "apple watch": "Apple",
    # Lenovo
    "thinkpad": "Lenovo", "ideapad": "Lenovo", "lenovo yoga": "Lenovo",
    "yoga slim": "Lenovo", "yoga pro": "Lenovo",
    "lenovo legion": "Lenovo", "legion 5": "Lenovo", "legion 7": "Lenovo",
    "thinkbook": "Lenovo",
    # HP
    "spectre": "HP", "envy": "HP", "omen": "HP", "pavilion": "HP",
    "probook": "HP", "elitebook": "HP", "zbook": "HP",
    # ASUS
    "zenbook": "ASUS", "vivobook": "ASUS", "rog": "ASUS", "tuf gaming": "ASUS",
    "expertbook": "ASUS", "proart": "ASUS",
    # Dell
    "xps": "Dell", "inspiron": "Dell", "alienware": "Dell",
    "latitude": "Dell", "vostro": "Dell",
    # Acer
    "acer swift": "Acer", "aspire": "Acer", "predator helios": "Acer",
    "acer nitro": "Acer", "nitro 5": "Acer", "nitro 7": "Acer",
    # MSI
    "msi stealth": "MSI", "msi creator": "MSI", "msi prestige": "MSI", "msi raider": "MSI",
    # Samsung
    "galaxy": "Samsung", "galaxy book": "Samsung",
    # Xiaomi / Redmi
    "redmi": "Xiaomi", "poco": "Xiaomi", "mi ": "Xiaomi",
    # OnePlus
    "oneplus": "OnePlus",
    # boAt
    "boat": "boAt",
    # Nothing
    "nothing phone": "Nothing", "cme ear": "Nothing",
}


def _detect_brand(text: str, brands: list[str]) -> str:
    text_lower = text.lower()
    # Direct brand name match first
    for brand in brands:
        if brand.lower() in text_lower:
            return brand
    # Alias match: longer aliases checked before shorter ones to avoid false partial hits
    for alias in sorted(_BRAND_ALIASES, key=len, reverse=True):
        if alias in text_lower:
            canonical = _BRAND_ALIASES[alias]
            # Only return if the canonical brand is in the requested brands list (or list is empty)
            if not brands or canonical in brands:
                return canonical
    return "Other"


def _is_relevant(text: str, keywords: list[str], brands: list[str]) -> bool:
    """True if the post mentions at least one keyword or a brand the user selected."""
    text_lower = text.lower()
    if any(kw.lower() in text_lower for kw in keywords):
        return True
    # _detect_brand already filters aliases against the user's brands list,
    # so this is brand-aware and won't match on generic words like "swift" or "yoga"
    if _detect_brand(text, brands) != "Other":
        return True
    return False


# ── Sample data loader ────────────────────────────────────────

def _load_sample_data(
    category: str,
    keywords: list[str],
    brands: list[str],
    date_from: str,
    date_to: str,
) -> pd.DataFrame:
    try:
        df = pd.read_csv(settings.SAMPLE_DATA_PATH)
        df = df[NORMALIZED_COLUMNS].copy()

        if "date" in df.columns and date_from and date_to:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            date_filtered = df[(df["date"] >= date_from) & (df["date"] <= date_to)]
            if len(date_filtered) >= 5:
                df = date_filtered
            else:
                logger.info("Sample data: date filter < 5 records — returning full sample for demo.")

        if brands:
            brand_mask = df["brand"].isin(brands) | (df["brand"] == "Other")
            df = df[brand_mask]

        if keywords:
            kw_lower = [k.lower() for k in keywords]
            mask = (
                df["text"].str.lower().apply(lambda t: any(k in t for k in kw_lower))
                | df["topic"].str.lower().apply(lambda t: any(k in t for k in kw_lower))
            )
            kw_filtered = df[mask]
            df = kw_filtered if len(kw_filtered) >= 5 else df

        df = df.reset_index(drop=True)
        logger.info(f"Loaded {len(df)} records from sample data")
        return df
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)
