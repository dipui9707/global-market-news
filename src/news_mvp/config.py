from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    streamlit_server_port: int
    default_lookback_hours: int
    default_page_size: int
    collector_item_limit: int
    article_retention_count: int
    auto_update_enabled: bool
    auto_update_interval_seconds: int
    translation_enabled: bool
    translation_api_key: str | None
    translation_model: str
    translation_endpoint_id: str | None
    translation_base_url: str
    translation_source_lang: str
    translation_target_lang: str
    translation_max_items_per_run: int
    story_dedup_lookback_hours: int

    @property
    def database_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            return ROOT_DIR / self.database_url.replace("sqlite:///", "", 1)
        raise ValueError("Only sqlite:/// DATABASE_URL is supported in Stage 1.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv(ENV_FILE)
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///data/news_mvp.db"),
        streamlit_server_port=int(os.getenv("STREAMLIT_SERVER_PORT", "8501")),
        default_lookback_hours=int(os.getenv("DEFAULT_LOOKBACK_HOURS", "72")),
        default_page_size=int(os.getenv("DEFAULT_PAGE_SIZE", "50")),
        collector_item_limit=int(os.getenv("COLLECTOR_ITEM_LIMIT", "20")),
        article_retention_count=int(os.getenv("ARTICLE_RETENTION_COUNT", "5000")),
        auto_update_enabled=os.getenv("AUTO_UPDATE_ENABLED", "false").lower() in {"1", "true", "yes", "on"},
        auto_update_interval_seconds=int(os.getenv("AUTO_UPDATE_INTERVAL_SECONDS", "300")),
        translation_enabled=os.getenv("TRANSLATION_ENABLED", "false").lower() in {"1", "true", "yes", "on"},
        translation_api_key=(
            os.getenv("TRANSLATION_API_KEY")
            or os.getenv("ARK_API_KEY")
            or os.getenv("DASHSCOPE_API_KEY")
            or None
        ),
        translation_model=os.getenv("TRANSLATION_MODEL", "doubao-seed-2.0-pro"),
        translation_endpoint_id=os.getenv("TRANSLATION_ENDPOINT_ID") or None,
        translation_base_url=os.getenv("TRANSLATION_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
        translation_source_lang=os.getenv("TRANSLATION_SOURCE_LANG", "auto"),
        translation_target_lang=os.getenv("TRANSLATION_TARGET_LANG", "Chinese"),
        translation_max_items_per_run=int(os.getenv("TRANSLATION_MAX_ITEMS_PER_RUN", "40")),
        story_dedup_lookback_hours=int(os.getenv("STORY_DEDUP_LOOKBACK_HOURS", "36")),
    )
