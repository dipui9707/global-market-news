from __future__ import annotations

import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    filtered_query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not k.startswith("utm_")]
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urlencode(filtered_query), ""))


def fingerprint_text(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


def make_article_id(source: str, url: str) -> str:
    return hashlib.sha1(f"{source}:{normalize_url(url)}".encode("utf-8")).hexdigest()
