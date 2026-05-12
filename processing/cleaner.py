import hashlib
import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)

_URL_RE = re.compile(r"https?://\S+")
_HTML_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["text"] = df["text"].fillna("").apply(clean_text)

    before = len(df)
    df = _filter_short(df, min_length=30)
    df = _deduplicate(df)
    logger.info(
        f"Cleaning: {before} → {len(df)} records "
        f"(removed {before - len(df)})"
    )
    return df.reset_index(drop=True)


def clean_text(text: str) -> str:
    text = _HTML_RE.sub(" ", text)
    text = _URL_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def _filter_short(df: pd.DataFrame, min_length: int = 30) -> pd.DataFrame:
    return df[df["text"].str.len() >= min_length]


def _deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    df["_hash"] = df["text"].apply(
        lambda t: hashlib.sha256(t.lower().strip().encode()).hexdigest()
    )
    df = df.drop_duplicates(subset="_hash")
    return df.drop(columns=["_hash"])
