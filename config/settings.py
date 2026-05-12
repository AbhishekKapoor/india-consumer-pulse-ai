import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


class Settings:
    # Apify
    APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")
    APIFY_REDDIT_ACTOR: str = os.getenv("APIFY_REDDIT_ACTOR", "trudax/reddit-scraper-lite")
    APIFY_YOUTUBE_ACTOR: str = os.getenv("APIFY_YOUTUBE_ACTOR", "streamers~youtube-scraper")
    APIFY_AMAZON_ACTOR: str = os.getenv("APIFY_AMAZON_ACTOR", "axesso_data/amazon-reviews-scraper")
    APIFY_NEWS_ACTOR: str = os.getenv("APIFY_NEWS_ACTOR", "apify~google-news-scraper")

    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
    OPENROUTER_CLASSIFICATION_MODEL: str = os.getenv(
        "OPENROUTER_CLASSIFICATION_MODEL",
        os.getenv("OPENROUTER_MODEL", "openrouter/auto"),
    )
    OPENROUTER_SUMMARY_MODEL: str = os.getenv(
        "OPENROUTER_SUMMARY_MODEL",
        os.getenv("OPENROUTER_MODEL", "openrouter/auto"),
    )

    # Pipeline
    MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "10"))
    MAX_TOKENS_CLASSIFY: int = int(os.getenv("MAX_TOKENS_CLASSIFY", "2000"))
    MAX_TOKENS_SUMMARY: int = int(os.getenv("MAX_TOKENS_SUMMARY", "4000"))

    # Paths — always absolute so they resolve regardless of working directory
    _ROOT: Path = Path(__file__).parent.parent
    RAW_DATA_DIR: str = str(_ROOT / "data" / "raw")
    PROCESSED_DATA_DIR: str = str(_ROOT / "data" / "processed")
    SAMPLE_DATA_PATH: str = str(_ROOT / "data" / "samples" / "sample_consumer_tech.csv")

    @property
    def apify_configured(self) -> bool:
        return bool(self.APIFY_API_TOKEN)

    @property
    def openrouter_configured(self) -> bool:
        return bool(self.OPENROUTER_API_KEY)


settings = Settings()
