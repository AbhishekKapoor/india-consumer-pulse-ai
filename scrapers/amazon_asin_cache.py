"""
Amazon ASIN Cache — India Consumer Pulse AI

Discovers top Amazon.in products per brand automatically and caches ASINs
so the review scraper always has URLs without manual maintenance.

Discovery runs when:
  - Cache is missing
  - Cache is older than CACHE_TTL_DAYS
  - A brand is requested that has no cached entry
"""

import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

from config.settings import settings

logger = logging.getLogger(__name__)

CACHE_PATH     = Path(settings.RAW_DATA_DIR).parent / "amazon_asins_cache.json"
CACHE_TTL_DAYS = 7

# Amazon.in search URL sorted by review count — finds the most-reviewed products first
_AMAZON_SEARCH_URL = (
    "https://www.amazon.in/s"
    "?k={query}"
    "&i=computers"           # Electronics > Computers category
    "&s=review-rank"         # sort by number of reviews
    "&rh=n%3A976392031"      # Electronics node
)

# Maps category to the product-type qualifier used in the discovery query
_CATEGORY_QUALIFIER = {
    "Consumer Tech India": "laptop OR smartphone OR earbuds",
    "laptops":             "laptop",
    "smartphones":         "smartphone",
    "wearables":           "smartwatch earbuds",
    "audio":               "headphones speaker",
}

# Regex to extract ASINs from Amazon.in HTML
_ASIN_RE = re.compile(r"/dp/([A-Z0-9]{10})")


# ── Public API ────────────────────────────────────────────────

def get_product_urls(brands: list[str], category: str) -> list[str]:
    """
    Return Amazon.in product URLs for the given brands.
    Loads from cache; auto-discovers for any brand that is missing or stale.
    """
    cache = _load_cache()
    stale_brands = _find_stale_brands(cache, brands)

    if stale_brands:
        logger.info(f"Amazon ASIN discovery needed for: {stale_brands}")
        discovered = _discover_asins(stale_brands, category)
        _update_cache(cache, discovered)

    urls: list[str] = []
    for brand in brands:
        brand_entry = cache.get("brands", {}).get(brand, {})
        urls.extend(brand_entry.get("urls", []))

    logger.info(f"Amazon: {len(urls)} product URLs for {len(brands)} brands (from cache)")
    return urls


# ── Cache helpers ─────────────────────────────────────────────

def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            pass
    return {"brands": {}}


def _find_stale_brands(cache: dict, brands: list[str]) -> list[str]:
    cutoff = datetime.now() - timedelta(days=CACHE_TTL_DAYS)
    stale = []
    for brand in brands:
        entry = cache.get("brands", {}).get(brand)
        if not entry:
            stale.append(brand)
            continue
        try:
            discovered_at = datetime.fromisoformat(entry.get("discovered_at", ""))
            if discovered_at < cutoff:
                stale.append(brand)
        except Exception:
            stale.append(brand)
    return stale


def _update_cache(cache: dict, discovered: dict[str, list[str]]) -> None:
    now = datetime.now().isoformat()
    cache.setdefault("brands", {})
    for brand, urls in discovered.items():
        cache["brands"][brand] = {"urls": urls, "discovered_at": now}
    cache["updated_at"] = now
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(cache, indent=2))
        logger.info(f"Amazon ASIN cache saved → {CACHE_PATH}")
    except Exception as e:
        logger.warning(f"Could not write ASIN cache: {e}")


# ── ASIN discovery ────────────────────────────────────────────

def _discover_asins(brands: list[str], category: str) -> dict[str, list[str]]:
    """
    Search Amazon.in for each brand and extract top product ASINs.
    Tries direct HTTP first (free). Falls back to Apify actor (uses proxy,
    bypasses blocks) automatically — no manual intervention needed.
    """
    results: dict[str, list[str]] = {}
    qualifier = _CATEGORY_QUALIFIER.get(category, "")

    for brand in brands:
        query = f"{brand} {qualifier}".strip().replace(" ", "+")
        url   = _AMAZON_SEARCH_URL.format(query=query)
        asins = _fetch_asins_direct(url, brand)

        if not asins:
            # Retry without category qualifier
            asins = _fetch_asins_direct(
                f"https://www.amazon.in/s?k={brand.replace(' ', '+')}&s=review-rank",
                brand,
            )

        if not asins:
            # Apify fallback — uses residential proxies, bypasses Amazon bot detection
            logger.info(f"Amazon direct blocked for '{brand}' — switching to Apify discovery")
            asins = _fetch_asins_via_apify(brand, category)

        urls = [f"https://www.amazon.in/dp/{asin}" for asin in asins[:5]]
        results[brand] = urls
        logger.info(f"Amazon discovery [{brand}]: {len(urls)} products found")
        time.sleep(1.5)

    return results


def _fetch_asins_direct(url: str, brand: str) -> list[str]:
    """Direct HTTP request to Amazon.in search — free, no proxies, may be blocked."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200 and "dp/" in resp.text:
            asins = list(dict.fromkeys(_ASIN_RE.findall(resp.text)))
            asins = [a for a in asins if not a.startswith("B00000")]
            return asins[:5]
        if resp.status_code in (503, 403, 429):
            logger.debug(f"Amazon.in returned {resp.status_code} for '{brand}'")
    except Exception as e:
        logger.debug(f"Amazon direct request failed for '{brand}': {e}")
    return []


def _fetch_asins_via_apify(brand: str, category: str) -> list[str]:
    """
    Apify-based ASIN discovery using amazon-scraper actor.
    Uses residential proxy rotation — handles Amazon bot detection reliably.
    Only called when direct requests are blocked. Costs Apify compute units
    for discovery only (runs once per brand per week, not on every pipeline run).
    """
    from config.settings import settings

    if not settings.apify_configured:
        logger.warning("Apify not configured — cannot use Apify fallback for Amazon discovery")
        return []

    qualifier = _CATEGORY_QUALIFIER.get(category, "laptop")
    query     = f"{brand} {qualifier} India"

    actor_input = {
        "searchQuery": query,
        "maxItems":    5,
        "country":     "IN",
        "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
    }

    # Local import to avoid circular dependency (apify_scraper imports this module)
    from scrapers.apify_scraper import _run_apify_actor

    items = _run_apify_actor("apify/amazon-scraper", actor_input)
    if not items:
        return []

    asins: list[str] = []
    for item in items:
        # Actor may return url, productUrl, or asin directly
        for field in ("url", "productUrl", "detailPageURL"):
            val = item.get(field, "")
            if val:
                m = _ASIN_RE.search(val)
                if m and m.group(1) not in asins:
                    asins.append(m.group(1))
                    break
        asin = item.get("asin", item.get("productAsin", ""))
        if asin and asin not in asins:
            asins.append(asin)

    logger.info(f"Apify discovery [{brand}]: {len(asins)} ASINs found")
    return asins[:5]
