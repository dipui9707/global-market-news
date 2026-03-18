from __future__ import annotations


def summarize_text(title: str, clean_text: str, raw_summary: str | None = None) -> str:
    candidate = raw_summary or clean_text or title
    if candidate:
        snippet = candidate[:220].strip()
        if snippet.lower() == title.lower() and clean_text:
            snippet = clean_text[:220].strip()
        return snippet + ("..." if len(candidate) > 220 else "")
    return title
