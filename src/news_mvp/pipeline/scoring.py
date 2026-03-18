from __future__ import annotations

from datetime import UTC, datetime


def score_article(
    source: str,
    event_type: str | None,
    asset_tag_count: int,
    published_at: str | None,
    is_duplicate: bool,
) -> float:
    source_weight = {
        "Reuters": 0.9,
        "Federal Reserve": 1.0,
        "BLS": 1.0,
    }.get(source, 0.5)
    event_weight = {
        "policy": 0.3,
        "data": 0.25,
        "breaking": 0.2,
    }.get(event_type, 0.1)
    asset_weight = min(asset_tag_count * 0.08, 0.24)
    recency_bonus = 0.0
    if published_at:
        try:
            age_hours = (datetime.now(UTC) - datetime.fromisoformat(published_at)).total_seconds() / 3600
            recency_bonus = max(0.0, 0.25 - min(age_hours / 72, 0.25))
        except ValueError:
            recency_bonus = 0.0
    duplicate_penalty = -0.4 if is_duplicate else 0.0
    return max(0.0, round((source_weight + event_weight + asset_weight + recency_bonus + duplicate_penalty) * 100, 2))
