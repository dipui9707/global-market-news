from __future__ import annotations

from collections.abc import Iterable
import re

import requests

from news_mvp.config import Settings
from news_mvp.db import connection_scope, update_article_translations, update_event_translation


HIDDEN_SOURCES = ("联合早报",)


def translation_is_configured(settings: Settings) -> bool:
    return settings.translation_enabled and bool(settings.dashscope_api_key)


def should_translate_text(*, text: str | None, language: str | None, existing_translation: str | None) -> bool:
    if existing_translation:
        return False
    normalized = (text or "").strip()
    if not normalized:
        return False
    if language and language.lower().startswith("zh"):
        return False
    if _contains_chinese(normalized):
        return False
    return True


def should_translate_title(*, title: str, language: str | None, existing_translation: str | None) -> bool:
    return should_translate_text(text=title, language=language, existing_translation=existing_translation)


def translate_text(text: str, settings: Settings) -> str | None:
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
            "messages": [{"role": "user", "content": text}],
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


def translate_title(title: str, settings: Settings) -> str | None:
    return translate_text(title, settings)


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
            summary,
            language,
            title_zh,
            summary_zh,
            e.id AS event_id,
            e.event_title,
            e.event_title_zh
        FROM articles
        LEFT JOIN article_event_map aem ON articles.id = aem.article_id
        LEFT JOIN events e ON aem.event_id = e.id
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
            summary = row["summary"]
            event_title = row["event_title"]

            title_zh = _translate_with_cache(
                translation_cache,
                title,
                settings,
                should_translate_text(text=title, language=row["language"], existing_translation=row["title_zh"]),
            )
            summary_zh = _translate_with_cache(
                translation_cache,
                summary,
                settings,
                should_translate_text(text=summary, language=row["language"], existing_translation=row["summary_zh"]),
            )
            event_title_zh = _translate_with_cache(
                translation_cache,
                event_title,
                settings,
                should_translate_text(text=event_title, language=row["language"], existing_translation=row["event_title_zh"]),
            )

            if title_zh or summary_zh:
                update_article_translations(
                    connection,
                    row["id"],
                    title_zh=title_zh,
                    summary_zh=summary_zh,
                )
            if event_title_zh and row["event_id"]:
                update_event_translation(connection, row["event_id"], event_title_zh)

            translated_count += sum(1 for value in (title_zh, summary_zh, event_title_zh) if value)

    return translated_count


def _contains_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def _translate_with_cache(
    translation_cache: dict[str, str | None],
    text: str | None,
    settings: Settings,
    should_translate: bool,
) -> str | None:
    if not should_translate:
        return None
    normalized = (text or "").strip()
    if not normalized:
        return None
    if normalized in translation_cache:
        return translation_cache[normalized]
    try:
        translation = translate_text(normalized, settings)
    except requests.RequestException:
        translation = None
    translation_cache[normalized] = translation
    return translation
