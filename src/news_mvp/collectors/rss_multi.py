from __future__ import annotations

from news_mvp.collectors.base import (
    ArticlePayload,
    BaseCollector,
    html_to_text,
    normalize_title,
    parse_entry_published,
    parse_feed,
    utc_now_iso,
)
from news_mvp.config import Settings


class MultiFeedRSSCollector(BaseCollector):
    name = ""
    source_name = ""
    source_type = "media"
    feed_urls: tuple[str, ...] = ()
    region = "Global"
    language = "en"

    def _make_payload(
        self,
        *,
        title: str,
        url: str,
        published_at: str | None,
        fetched_at: str,
        summary: str,
    ) -> ArticlePayload:
        return ArticlePayload(
            source=self.source_name,
            source_type=self.source_type,
            title=title,
            url=url,
            published_at=published_at,
            fetched_at=fetched_at,
            language=self.language,
            summary=summary,
            raw_text=summary,
            region=self.region,
        )

    def collect(self, settings: Settings) -> list[ArticlePayload]:
        fetched_at = utc_now_iso()
        items: list[ArticlePayload] = []
        seen_keys: set[tuple[str, str]] = set()

        for feed_url in self.feed_urls:
            feed = parse_feed(feed_url)
            for entry in feed.entries[: settings.collector_item_limit]:
                title = normalize_title(entry.get("title", ""))
                url = entry.get("link", "").strip()
                if not title or not url:
                    continue

                dedup_key = (title.lower(), url)
                if dedup_key in seen_keys:
                    continue
                seen_keys.add(dedup_key)

                summary = html_to_text(entry.get("summary") or entry.get("description"))
                items.append(
                    self._make_payload(
                        title=title,
                        url=url,
                        published_at=parse_entry_published(entry),
                        fetched_at=fetched_at,
                        summary=summary,
                    )
                )

        return items[: settings.collector_item_limit]
