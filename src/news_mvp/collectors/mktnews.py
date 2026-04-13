from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any

import requests

from news_mvp.collectors.base import ArticlePayload, BaseCollector, utc_now_iso
from news_mvp.config import ROOT_DIR, Settings


REST_FLASH_URL = "https://api.mktnews.net/api/flash"
PAGE_URL = "https://mktnews.net/flash.html"
DETAIL_URL_TEMPLATE = "https://mktnews.com/flashDetail.html?id={item_id}"
HTML_TAG_RE = re.compile(r"<[^>]+>")


def parse_mktnews_timestamp(raw_time: str | None) -> str | None:
    if not raw_time:
        return None
    try:
        return datetime.fromisoformat(raw_time.replace("Z", "+00:00")).astimezone(UTC).isoformat()
    except ValueError:
        return None


def clean_mktnews_text(raw_text: str | None) -> str:
    text = HTML_TAG_RE.sub(" ", raw_text or "")
    return " ".join(text.split())


def extract_mktnews_content(entry: dict[str, Any]) -> str:
    payload = entry.get("data") or {}
    return clean_mktnews_text(payload.get("content") or payload.get("title") or "")


def normalize_mktnews_entry(entry: dict[str, Any], fetched_at: str) -> ArticlePayload | None:
    if entry.get("type") != 0:
        return None

    item_id = entry.get("id")
    if not item_id:
        return None

    content = extract_mktnews_content(entry)
    if not content:
        return None

    return ArticlePayload(
        source="MktNews",
        source_type="media",
        title=content,
        url=DETAIL_URL_TEMPLATE.format(item_id=item_id),
        published_at=parse_mktnews_timestamp(entry.get("time")),
        fetched_at=fetched_at,
        language="en",
        summary=None,
        raw_text=content,
        region="Global",
    )


def fetch_mktnews_flash(limit: int, timeout: int = 20) -> list[dict[str, Any]]:
    response = requests.get(
        REST_FLASH_URL,
        params={"limit": limit},
        headers={
            "Accept": "application/json, text/plain, */*",
            "Referer": PAGE_URL,
            "User-Agent": "Mozilla/5.0",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        data = data.get("data")
    if not isinstance(data, list):
        raise ValueError("Unexpected MktNews API response format.")
    return data


def load_mktnews_cache(cache_path: Path) -> list[dict[str, Any]]:
    if not cache_path.exists():
        return []
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(payload, dict):
        return []
    items = payload.get("items")
    if not isinstance(items, list):
        return []
    return [entry for entry in items if isinstance(entry, dict)]


def merge_mktnews_entries(
    cache_entries: list[dict[str, Any]],
    api_entries: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for entry in [*cache_entries, *api_entries]:
        item_id = entry.get("id")
        if not item_id:
            continue
        existing = merged.get(item_id)
        if existing is None:
            merged[item_id] = entry
            continue
        existing_time = parse_mktnews_timestamp(existing.get("time"))
        current_time = parse_mktnews_timestamp(entry.get("time"))
        if current_time and (existing_time is None or current_time > existing_time):
            merged[item_id] = entry

    def sort_key(entry: dict[str, Any]) -> tuple[int, str]:
        published_at = parse_mktnews_timestamp(entry.get("time"))
        return (0 if published_at else 1, published_at or "")

    sorted_entries = sorted(merged.values(), key=sort_key, reverse=True)
    return sorted_entries[:limit]


class MktNewsCollector(BaseCollector):
    name = "mktnews"
    source_name = "MktNews"

    def collect(self, settings: Settings) -> list[ArticlePayload]:
        cache_path = ROOT_DIR / settings.mktnews_live_cache_path
        cache_entries = load_mktnews_cache(cache_path)

        api_entries: list[dict[str, Any]] = []
        try:
            api_entries = fetch_mktnews_flash(limit=max(settings.collector_item_limit, 50))
        except (requests.RequestException, ValueError):
            if not cache_entries:
                return []

        fetched_at = utc_now_iso()
        merged_entries = merge_mktnews_entries(
            cache_entries=cache_entries,
            api_entries=api_entries,
            limit=settings.collector_item_limit,
        )

        items: list[ArticlePayload] = []
        for entry in merged_entries:
            payload = normalize_mktnews_entry(entry, fetched_at=fetched_at)
            if payload is not None:
                items.append(payload)
        return items
