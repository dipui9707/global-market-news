from __future__ import annotations

from dataclasses import dataclass
import calendar
from datetime import datetime, UTC
from email.utils import parsedate_to_datetime
from html import unescape
import re
from typing import Any, Protocol

import feedparser

from news_mvp.config import Settings


@dataclass(slots=True)
class ArticlePayload:
    source: str
    source_type: str
    title: str
    url: str
    published_at: str | None
    fetched_at: str
    language: str = "en"
    summary: str | None = None
    raw_text: str | None = None
    region: str | None = None


class BaseCollector(Protocol):
    name: str

    def collect(self, settings: Settings) -> list[ArticlePayload]:
        ...


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def parse_feed(url: str) -> feedparser.FeedParserDict:
    try:
        return feedparser.parse(url)
    except Exception:
        return feedparser.parse("")


def parse_published(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(UTC).isoformat()
    except (TypeError, ValueError, IndexError):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC).isoformat()
        except ValueError:
            return None


def parse_entry_published(entry: Any) -> str | None:
    for key in ("published", "updated", "created"):
        value = entry.get(key) if hasattr(entry, "get") else getattr(entry, key, None)
        parsed_value = parse_published(value)
        if parsed_value:
            return parsed_value

    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        value = entry.get(key) if hasattr(entry, "get") else getattr(entry, key, None)
        if not value:
            continue
        try:
            timestamp = calendar.timegm(value)
            return datetime.fromtimestamp(timestamp, UTC).isoformat()
        except (TypeError, ValueError, OverflowError):
            continue
    return None


def html_to_text(value: str | None) -> str:
    if not value:
        return ""
    return sanitize_text(value)


def normalize_title(value: str) -> str:
    title = sanitize_text(value)
    title = re.sub(r"\s+-\s+Reuters$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+\|\s+.*$", "", title)
    return title.strip()


def sanitize_text(value: str | None) -> str:
    if not value:
        return ""

    text = value
    for _ in range(2):
        text = unescape(text)
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?is)<!DOCTYPE.*?>", " ", text)
    text = re.sub(r"(?is)<html.*?>|</html>|<body.*?>|</body>|<head.*?>|</head>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"(?i)\b(function|window|document)\b\s*[\.\(=][^\n]{0,120}", " ", text)
    text = text.replace("\u00a0", " ")
    text = " ".join(text.split())
    return text.strip()
