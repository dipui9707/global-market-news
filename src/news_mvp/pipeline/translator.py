from __future__ import annotations

from collections.abc import Iterable
import re

import requests

from news_mvp.config import Settings
from news_mvp.db import connection_scope, update_article_translations


HIDDEN_SOURCES = ("联合早报",)


def translation_is_configured(settings: Settings) -> bool:
    return settings.translation_enabled and bool(settings.translation_api_key)


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

    model_name = settings.translation_endpoint_id or settings.translation_model
    if settings.translation_model.startswith("qwen-mt-"):
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": text,
                }
            ],
            "translation_options": {
                "source_lang": settings.translation_source_lang,
                "target_lang": settings.translation_target_lang,
            },
        }
    else:
        payload = {
            "model": model_name,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是专业财经新闻翻译助手。"
                        "请把用户提供的一条新闻标题翻译成简洁、准确、自然的简体中文财经标题。"
                        "保留公司名、机构名、缩写、数字、货币、百分比、合约月份和专有名词。"
                        "不要补充解释，不要扩写，不要输出引号，只输出翻译结果。"
                    ),
                },
                {"role": "user", "content": text},
            ],
        }

    response = requests.post(
        f"{settings.translation_base_url.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.translation_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        return None
    message = choices[0].get("message") or {}
    raw_content = message.get("content")
    if isinstance(raw_content, list):
        content = "".join(
            part.get("text", "")
            for part in raw_content
            if isinstance(part, dict)
        ).strip()
    else:
        content = (raw_content or "").strip()
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

            title_zh = _translate_with_cache(
                translation_cache,
                title,
                settings,
                should_translate_text(text=title, language=row["language"], existing_translation=row["title_zh"]),
            )

            if title_zh:
                update_article_translations(
                    connection,
                    row["id"],
                    title_zh=title_zh,
                )
                translated_count += 1

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
