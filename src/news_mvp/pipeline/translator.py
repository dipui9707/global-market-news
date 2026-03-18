from __future__ import annotations

from collections.abc import Iterable
import re

import requests

from news_mvp.config import Settings
from news_mvp.db import connection_scope, update_article_translation


HIDDEN_SOURCES = ("联合早报",)


def translation_is_configured(settings: Settings) -> bool:
    return settings.translation_enabled and bool(settings.dashscope_api_key)


def should_translate_title(*, title: str, language: str | None, existing_translation: str | None) -> bool:
    if existing_translation:
        return False
    normalized = title.strip()
    if not normalized:
        return False
    if language and language.lower().startswith("zh"):
        return False
    if _contains_chinese(normalized):
        return False
    return True


def translate_title(title: str, settings: Settings) -> str | None:
    if not translation_is_configured(settings):
        return None

    response = requests.post(
        f"{settings.translation_base_url.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.dashscope_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.translation_model,
            "messages": [{"role": "user", "content": title}],
            "translation_options": {
                "source_lang": settings.translation_source_lang,
                "target_lang": settings.translation_target_lang,
                "domains": "finance",
            },
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        return None
    message = choices[0].get("message") or {}
    content = (message.get("content") or "").strip()
    return content or None


def iter_titles_to_translate(
    items: Iterable[tuple[str, str | None, str | None]],
    settings: Settings,
) -> list[str]:
    titles: list[str] = []
    for title, language, existing_translation in items:
        if not should_translate_title(title=title, language=language, existing_translation=existing_translation):
            continue
        titles.append(title)
        if len(titles) >= settings.translation_max_items_per_run:
            break
    return titles


def backfill_recent_translations(settings: Settings, hours: int, limit: int) -> int:
    if not translation_is_configured(settings):
        return 0

    query = f"""
        SELECT
            id,
            title,
            language,
            title_zh
        FROM articles
        WHERE COALESCE(published_at, fetched_at) >= datetime('now', ?)
          AND source NOT IN ({", ".join("?" for _ in HIDDEN_SOURCES)})
        ORDER BY importance_score DESC, COALESCE(published_at, fetched_at) DESC
    """
    params = [f"-{hours} hours", *HIDDEN_SOURCES]

    translated_count = 0
    translation_cache: dict[str, str | None] = {}

    with connection_scope(settings) as connection:
        rows = connection.execute(query, params).fetchall()
        for row in rows:
            if translated_count >= limit:
                break

            title = row["title"]
            if not should_translate_title(
                title=title,
                language=row["language"],
                existing_translation=row["title_zh"],
            ):
                continue

            if title in translation_cache:
                translation = translation_cache[title]
            else:
                try:
                    translation = translate_title(title, settings)
                except requests.RequestException:
                    translation = None
                translation_cache[title] = translation

            if not translation:
                continue

            update_article_translation(connection, row["id"], translation)
            translated_count += 1

    return translated_count


def _contains_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))
