from __future__ import annotations

import hashlib
import re
from collections import Counter
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


STORY_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "after",
    "amid",
    "says",
    "say",
    "as",
    "to",
    "of",
    "on",
    "in",
    "over",
    "under",
    "latest",
    "update",
    "updates",
    "live",
    "news",
    "report",
    "reports",
    "reportedly",
}


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    filtered_query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not k.startswith("utm_")]
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urlencode(filtered_query), ""))


def fingerprint_text(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


def make_article_id(source: str, url: str) -> str:
    return hashlib.sha1(f"{source}:{normalize_url(url)}".encode("utf-8")).hexdigest()


def build_story_key(title: str, summary: str | None = None, clean_text: str | None = None) -> str | None:
    weighted_tokens = (
        _extract_story_tokens(title) * 3
        + _extract_story_tokens(summary or "") * 2
        + _extract_story_tokens((clean_text or "")[:320])
    )
    if not weighted_tokens:
        return None

    token_counts = Counter(weighted_tokens)
    ranked_tokens = sorted(
        token_counts.items(),
        key=lambda item: (-item[1], -len(item[0]), item[0]),
    )
    selected_tokens = [token for token, _ in ranked_tokens[:6]]
    if len(selected_tokens) < 3:
        return None
    return "-".join(selected_tokens)


def _extract_story_tokens(text: str) -> list[str]:
    tokens = []
    for token in re.findall(r"[a-z0-9%]+", text.lower()):
        if token in STORY_STOPWORDS:
            continue
        if token.isdigit() and len(token) < 4:
            continue
        if len(token) < 3:
            continue
        tokens.append(token)
    return tokens
