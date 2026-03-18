from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(slots=True)
class EventAssignment:
    event_key: str | None
    event_title: str | None


STOPWORDS = {
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
}


def assign_event(title: str, clean_text: str) -> EventAssignment:
    text = f"{title} {clean_text}".lower()
    words = [word for word in re.findall(r"[a-zA-Z]{3,}", text) if word not in STOPWORDS]
    if not words:
        return EventAssignment(event_key=None, event_title=title[:120] if title else None)
    key_terms = "-".join(words[:5])
    event_key = key_terms[:80]
    event_title = title[:120] if title else key_terms.replace("-", " ").title()
    return EventAssignment(event_key=event_key, event_title=event_title)
