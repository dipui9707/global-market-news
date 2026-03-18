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


class ReutersCollector(BaseCollector):
    name = "reuters"
    feed_url = (
        "https://news.google.com/rss/search?q=site%3Areuters.com%20"
        "(markets%20OR%20economy%20OR%20fed%20OR%20inflation)%20when%3A7d"
        "&hl=en-US&gl=US&ceid=US%3Aen"
    )

    def collect(self, settings: Settings) -> list[ArticlePayload]:
        feed = parse_feed(self.feed_url)
        fetched_at = utc_now_iso()
        items: list[ArticlePayload] = []
        for entry in feed.entries[: settings.collector_item_limit]:
            source = getattr(entry, "source", {}) or {}
            if source.get("title") and "Reuters" not in source.get("title", ""):
                continue
            items.append(
                ArticlePayload(
                    source="Reuters",
                    source_type="media",
                    title=normalize_title(entry.get("title", "")),
                    url=entry.get("link", ""),
                    published_at=parse_published(entry.get("published")),
                    fetched_at=fetched_at,
                    summary=html_to_text(entry.get("summary")),
                    raw_text=html_to_text(entry.get("summary")),
                    region="Global",
                )
            )
        return [item for item in items if item.title and item.url]
