from __future__ import annotations

from news_mvp.config import get_settings
from news_mvp.pipeline.orchestrator import run_pipeline
from news_mvp.pipeline.translator import backfill_recent_translations, translation_is_configured


def main() -> None:
    settings = get_settings()
    result = run_pipeline(settings)
    print("Pipeline status:", result.status)
    print("Message:", result.message)
    print("Collected:", result.collected_count)
    print("Stored:", result.stored_count)
    print("Duplicates:", result.duplicate_count)

    # 补翻遗留：单轮翻译预算（TRANSLATION_MAX_ITEMS_PER_RUN）小于新文章数时，
    # 超出预算的文章入库后 RSS 不再返回，会永久遗漏翻译。
    # 这里对最近时间窗内仍未翻译的外文标题做批量补翻（1 次请求/批）。
    if translation_is_configured(settings):
        backfilled = backfill_recent_translations(
            settings,
            hours=settings.default_lookback_hours,
            limit=settings.translation_max_items_per_run,
        )
        if backfilled:
            print("Backfilled translations:", backfilled)


if __name__ == "__main__":
    main()
