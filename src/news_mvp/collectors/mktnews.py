from __future__ import annotations

from datetime import UTC, datetime
import re

import requests

from news_mvp.collectors.base import ArticlePayload, BaseCollector, utc_now_iso
from news_mvp.config import Settings


class MktNewsCollector(BaseCollector):
    name = "mktnews"
    feed_url = "https://static.mktnews.net/json/flash/en.json"
    source_name = "MktNews"

    def collect(self, settings: Settings) -> list[ArticlePayload]:
        try:
            response = requests.get(
                self.feed_url,
                params={"t": int(datetime.now(UTC).timestamp())},
                headers={
                    "Accept": "application/json, text/plain, */*",
                    "Referer": "https://mktnews.net/flash.html",
                    "User-Agent": "Mozilla/5.0",
                },
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError):
            return []
        fetched_at = utc_now_iso()
        items: list[ArticlePayload] = []

        for entry in data[: settings.collector_item_limit]:
            if entry.get("type") != 0:
                continue
            content = ((entry.get("data") or {}).get("content") or "").strip()
            clean_content = re.sub(r"<[^>]+>", " ", content)
            clean_content = " ".join(clean_content.split())
            item_id = entry.get("id")
            if not clean_content or not item_id:
                continue

            published_at = None
            raw_time = entry.get("time")
            if raw_time:
                try:
                    published_at = datetime.fromisoformat(raw_time.replace("Z", "+00:00")).astimezone(UTC).isoformat()
                except ValueError:
                    published_at = None

            items.append(
                ArticlePayload(
                    source=self.source_name,
                    source_type="media",
                    title=clean_content,
                    url=f"https://mktnews.com/flashDetail.html?id={item_id}",
                    published_at=published_at,
                    fetched_at=fetched_at,
                    language="en",
                    summary=None,
                    raw_text=clean_content,
                    region="Global",
                )
            )

        return items
