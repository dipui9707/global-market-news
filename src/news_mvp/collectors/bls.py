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


class BLSCollector(BaseCollector):
    name = "bls"
    feed_url = (
        "https://news.google.com/rss/search?q=site%3Abls.gov%20"
        "(CPI%20OR%20PPI%20OR%20employment%20OR%20payrolls%20OR%20inflation)%20when%3A30d"
        "&hl=en-US&gl=US&ceid=US%3Aen"
    )

    def collect(self, settings: Settings) -> list[ArticlePayload]:
        feed = parse_feed(self.feed_url)
        fetched_at = utc_now_iso()
        items: list[ArticlePayload] = []
        for entry in feed.entries[: settings.collector_item_limit]:
            source = getattr(entry, "source", {}) or {}
            source_title = source.get("title", "")
            if "Labor Statistics" not in source_title and "BLS" not in source_title:
                continue
            items.append(
                ArticlePayload(
                    source="BLS",
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
