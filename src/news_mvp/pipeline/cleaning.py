from __future__ import annotations

from dataclasses import dataclass
import re

from news_mvp.collectors.base import sanitize_text


@dataclass(slots=True)
class CleaningResult:
    clean_text: str


def clean_text(raw_text: str | None) -> CleaningResult:
    if not raw_text:
        return CleaningResult(clean_text="")
    normalized = sanitize_text(raw_text)
    normalized = re.sub(r"\s+-\s+(Reuters|Bureau of Labor Statistics.*)$", "", normalized, flags=re.IGNORECASE)
    return CleaningResult(clean_text=normalized)
