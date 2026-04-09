from __future__ import annotations

from news_mvp.config import get_settings
from news_mvp.pipeline.translator import backfill_recent_translations


def main() -> None:
    settings = get_settings()
    translated = backfill_recent_translations(
        settings,
        hours=settings.default_lookback_hours,
        limit=settings.translation_max_items_per_run,
    )
    print("Translation backfill status: success")
    print("Translated titles:", translated)


if __name__ == "__main__":
    main()
