from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
import json
import re
import sqlite3
import time

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


# 标题翻译时截断到该长度：部分源（如 MktNews 综合快讯）的"标题"实际是全文摘要，
# 可达 900+ 字符，整条翻译输出极长，会拖慢/超时整批请求导致整批失败
MAX_TITLE_TRANSLATE_CHARS = 300


def _truncate_title(text: str) -> str:
    text = (text or "").strip()
    if len(text) <= MAX_TITLE_TRANSLATE_CHARS:
        return text
    return text[:MAX_TITLE_TRANSLATE_CHARS].rstrip() + "…"


def translate_text(text: str, settings: Settings) -> str | None:
    if not translation_is_configured(settings):
        return None
    text = _truncate_title(text)
    try:
        if settings.translation_provider == "deepl":
            result = _translate_with_deepl(text, settings)
        else:
            result = _translate_with_openai_compatible(text, settings)
    except requests.RequestException:
        result = None
    if result:
        return result
    return _translate_fallback_text(text, settings)


def _fallback_settings(settings: Settings) -> Settings | None:
    """若配置了备用翻译，返回构造好的备用 Settings；否则 None。"""
    if not settings.fallback_api_key:
        return None
    return replace(
        settings,
        translation_provider=(settings.fallback_provider or "deepl").lower(),
        translation_api_key=settings.fallback_api_key,
        translation_base_url=settings.fallback_base_url or settings.translation_base_url,
        translation_model=settings.fallback_model or settings.translation_model,
        translation_target_lang=settings.fallback_target_lang or settings.translation_target_lang,
    )


def _translate_fallback_text(text: str, settings: Settings) -> str | None:
    fallback = _fallback_settings(settings)
    if fallback is None:
        return None
    try:
        if fallback.translation_provider == "deepl":
            return _translate_with_deepl(text, fallback)
        return _translate_with_openai_compatible(text, fallback)
    except requests.RequestException:
        return None


def _translate_with_deepl(text: str, settings: Settings) -> str | None:
    data: dict[str, str] = {
        "text": text,
        "target_lang": settings.translation_target_lang,
    }
    source_lang = settings.translation_source_lang
    if source_lang and source_lang.lower() not in {"auto", ""}:
        data["source_lang"] = source_lang
    response = requests.post(
        settings.translation_base_url,
        headers={"Authorization": f"DeepL-Auth-Key {settings.translation_api_key}"},
        data=data,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    translations = payload.get("translations") or []
    if not translations:
        return None
    content = (translations[0].get("text") or "").strip()
    return content or None


def _translate_with_openai_compatible(text: str, settings: Settings) -> str | None:
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


def _batch_with_retry(
    titles: list[str],
    settings: Settings,
    retries: int = 1,
    backoff_seconds: float = 2.0,
    timeout: float = 20.0,
) -> list[str | None]:
    """批量翻译，失败时重试（免费模型如硅基流动 Hunyuan-MT-7B 抖动常见）。"""
    last: list[str | None] = [None] * len(titles)
    for attempt in range(retries + 1):
        if settings.translation_provider == "deepl":
            last = _batch_with_deepl(titles, settings)
        else:
            last = _batch_with_openai(titles, settings, timeout=timeout)
        if any(last):
            return last
        if attempt < retries:
            time.sleep(backoff_seconds)
    return last


def translate_titles_batch(titles: list[str], settings: Settings) -> list[str | None]:
    """批量翻译多条标题，返回与输入等长的列表（失败项为 None）。

    - DeepL：原生批量（一次请求多条）
    - OpenAI 兼容：一次请求传入 JSON 数组，要求按序返回 JSON 数组；解析失败则回退逐条
    - 主模型失败自动重试 1 次，再切换备用翻译（免费模型抖动时重试成功率很高）
    - 备用模型（如 DeepSeek 推理模型）较慢，使用更长超时
    """
    if not translation_is_configured(settings) or not titles:
        return [None] * len(titles)

    # 截断超长“标题”（整篇摘要），避免输出极长拖慢整批请求导致超时
    titles = [_truncate_title(t) for t in titles]

    primary = _batch_with_retry(titles, settings, timeout=15.0)
    if any(primary):
        return primary

    # 主翻译整批失败 → 备用翻译
    fallback = _fallback_settings(settings)
    if fallback is None:
        return primary
    if fallback.translation_provider == "deepl":
        return _batch_with_deepl(titles, fallback)
    return _batch_with_retry(titles, fallback, timeout=30.0)


def _batch_with_deepl(titles: list[str], settings: Settings) -> list[str | None]:
    data: dict[str, object] = {
        "text": titles,
        "target_lang": settings.translation_target_lang,
    }
    source_lang = settings.translation_source_lang
    if source_lang and source_lang.lower() not in {"auto", ""}:
        data["source_lang"] = source_lang
    try:
        response = requests.post(
            settings.translation_base_url,
            headers={"Authorization": f"DeepL-Auth-Key {settings.translation_api_key}"},
            data=data,
            timeout=30,
        )
        response.raise_for_status()
        results: list[str | None] = []
        for item in (response.json().get("translations") or []):
            results.append((item.get("text") or "").strip() or None)
        return results
    except requests.RequestException:
        return [None] * len(titles)


def _extract_json_array(content: str) -> list[str] | None:
    """从模型输出中提取 JSON 字符串数组（容忍 ```json 代码块等）。"""
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S)
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(x) for x in data]
    except (ValueError, TypeError):
        pass
    match = re.search(r"\[.*?\]", text, re.S)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return [str(x) for x in data]
        except (ValueError, TypeError):
            pass
    return None


def _batch_with_openai(titles: list[str], settings: Settings, timeout: float = 45.0) -> list[str | None]:
    # 特化的 qwen-mt 翻译接口不支持本批量协议，回退逐条
    if settings.translation_model.startswith("qwen-mt-"):
        return [translate_text(t, settings) for t in titles]
    model_name = settings.translation_endpoint_id or settings.translation_model
    payload = {
        "model": model_name,
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是专业财经新闻翻译助手。"
                    "我会给你一个 JSON 数组，包含若干条英文新闻标题。"
                    "请把每条翻译成简洁、准确、自然的简体中文财经标题。"
                    "保留公司名、机构名、缩写、数字、货币、百分比、合约月份和专有名词。"
                    "不要补充解释，不要扩写。"
                    "必须输出一个 JSON 数组，长度与输入一致，顺序一致，每个元素是翻译后的中文标题字符串。"
                ),
            },
            {"role": "user", "content": json.dumps(titles, ensure_ascii=False)},
        ],
    }
    try:
        response = requests.post(
            f"{settings.translation_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.translation_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            return [None] * len(titles)
        message = choices[0].get("message") or {}
        raw_content = message.get("content")
        if isinstance(raw_content, list):
            raw_content = "".join(
                part.get("text", "") for part in raw_content if isinstance(part, dict)
            )
        extracted = _extract_json_array(raw_content or "")
        if extracted is None or len(extracted) != len(titles):
            # 不逐条回退：会把 1 个批量请求放大成 N 次单条请求，
            # 打爆 Gemini 免费层配额（曾导致 429 持续数小时）。
            # 整批留待下一轮 cron 重试。
            return [None] * len(titles)
        return [str(item).strip() or None for item in extracted]
    except requests.RequestException:
        return [None] * len(titles)


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

    with connection_scope(settings) as connection:
        rows = connection.execute(query, params).fetchall()
        pending_ids: list[str] = []
        pending_titles: list[str] = []
        for row in rows:
            if len(pending_titles) >= limit:
                break
            if should_translate_text(
                text=row["title"],
                language=row["language"],
                existing_translation=row["title_zh"],
            ):
                pending_ids.append(row["id"])
                pending_titles.append(row["title"])

        if not pending_titles:
            return 0

        # 批量翻译（1 次请求/批），主失败自动切换备用翻译
        results = translate_titles_batch(pending_titles, settings)
        translated_count = 0
        for article_id, title_zh in zip(pending_ids, results):
            if not title_zh:
                continue
            # 写库可能与其他进程（cron pipeline / 页面按钮）并发冲突，
            # 遇到 database is locked 时短暂重试
            for attempt in range(4):
                try:
                    update_article_translations(connection, article_id, title_zh=title_zh)
                    translated_count += 1
                    break
                except sqlite3.OperationalError:
                    if attempt == 3:
                        raise
                    time.sleep(1.0 * (attempt + 1))

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
