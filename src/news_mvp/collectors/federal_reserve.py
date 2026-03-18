from __future__ import annotations

from news_mvp.collectors.base import (
    ArticlePayload,
    BaseCollector,
    html_to_text,
    normalize_title,
    parse_feed,
    parse_published,
    utc_now_iso,
)
from news_mvp.config import Settings


class FederalReserveCollector(BaseCollector):
    name = "federal_reserve"
    feed_url = "https://www.federalreserve.gov/feeds/press_all.xml"

    def collect(self, settings: Settings) -> list[ArticlePayload]:
        feed = parse_feed(self.feed_url)
        fetched_at = utc_now_iso()
        items: list[ArticlePayload] = []
        for entry in feed.entries[: settings.collector_item_limit]:
            items.append(
                ArticlePayload(
                    source="Federal Reserve",
                    source_type="official",
                    title=normalize_title(entry.get("title", "")),
                    url=entry.get("link", ""),
                    published_at=parse_published(entry.get("published")),
                    fetched_at=fetched_at,
                    summary=html_to_text(entry.get("summary")),
                    raw_text=html_to_text(entry.get("summary")),
                    region="United States",
                )
            )
        return [item for item in items if item.title and item.url]
