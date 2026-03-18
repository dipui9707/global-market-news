from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import requests
from uuid import uuid4

from news_mvp.collectors import (
    AxiosCollector,
    BLSCollector,
    BloombergCollector,
    CNBCCollector,
    CNNCollector,
    FTCollector,
    FederalReserveCollector,
    MktNewsCollector,
    ReutersCollector,
    SCMPCollector,
    WSJCollector,
    YahooFinanceCollector,
)
from news_mvp.config import Settings
from news_mvp.db import (
    connection_scope,
    fetch_article_by_content_hash,
    fetch_article_by_url,
    initialize_database,
    link_article_event,
    prune_articles,
    replace_article_tags,
    upsert_article,
    upsert_event,
)
from news_mvp.pipeline.cleaning import clean_text
from news_mvp.pipeline.clustering import assign_event
from news_mvp.pipeline.dedup import fingerprint_text, make_article_id, normalize_url
from news_mvp.pipeline.scoring import score_article
from news_mvp.pipeline.summarizer import summarize_text
from news_mvp.pipeline.tagging import infer_tags
from news_mvp.pipeline.translator import should_translate_title, translate_title, translation_is_configured


@dataclass(slots=True)
class PipelineRunResult:
    status: str
    message: str
    collected_count: int = 0
    stored_count: int = 0
    duplicate_count: int = 0


def get_collectors() -> list[object]:
    return [
        ReutersCollector(),
        BloombergCollector(),
        CNBCCollector(),
        CNNCollector(),
        WSJCollector(),
        FTCollector(),
        YahooFinanceCollector(),
        AxiosCollector(),
        SCMPCollector(),
        MktNewsCollector(),
        FederalReserveCollector(),
        BLSCollector(),
    ]


def list_collectors() -> list[str]:
    return [collector.name for collector in get_collectors()]


def run_pipeline(settings: Settings) -> PipelineRunResult:
    initialize_database(settings)
    payloads = []
    for collector in get_collectors():
        payloads.extend(collector.collect(settings))
    payloads.sort(
        key=lambda payload: payload.published_at or payload.fetched_at or "",
        reverse=True,
    )

    collected_count = len(payloads)
    stored_count = 0
    duplicate_count = 0
    translated_count = 0
    pruned_count = 0
    translation_cache: dict[str, str | None] = {}

    with connection_scope(settings) as connection:
        pending_translation_budget = settings.translation_max_items_per_run if translation_is_configured(settings) else 0

        for payload in payloads:
            normalized_url = normalize_url(payload.url)
            cleaning_result = clean_text(payload.raw_text or payload.summary or payload.title)
            clean_body = cleaning_result.clean_text or payload.title
            content_hash = fingerprint_text(f"{payload.title} {clean_body}")

            existing_by_url = fetch_article_by_url(connection, normalized_url)
            existing_by_hash = fetch_article_by_content_hash(connection, content_hash)
            is_duplicate = existing_by_url is not None or existing_by_hash is not None
            if is_duplicate:
                duplicate_count += 1

            tags = infer_tags(payload.title, clean_body)
            region = payload.region or next((tag.tag_name for tag in tags if tag.tag_type == "region"), None)
            event_type = next((tag.tag_name for tag in tags if tag.tag_type == "event_type"), None)
            asset_tag_count = len([tag for tag in tags if tag.tag_type == "asset"])
            summary = summarize_text(payload.title, clean_body, payload.summary)
            event_assignment = assign_event(payload.title, clean_body)
            article_id = make_article_id(payload.source, normalized_url)

            duplicate_group_id = None
            if existing_by_hash is not None:
                duplicate_group_id = existing_by_hash["id"]
            elif existing_by_url is not None:
                duplicate_group_id = existing_by_url["id"]

            existing_title_zh = None
            if existing_by_hash is not None and existing_by_hash["title_zh"]:
                existing_title_zh = existing_by_hash["title_zh"]
            elif existing_by_url is not None and existing_by_url["title_zh"]:
                existing_title_zh = existing_by_url["title_zh"]

            title_zh = existing_title_zh
            if title_zh is None and payload.title in translation_cache:
                title_zh = translation_cache[payload.title]
            elif (
                title_zh is None
                and pending_translation_budget > 0
                and should_translate_title(
                    title=payload.title,
                    language=payload.language,
                    existing_translation=existing_title_zh,
                )
            ):
                try:
                    title_zh = translate_title(payload.title, settings)
                except requests.RequestException:
                    title_zh = None
                translation_cache[payload.title] = title_zh
                pending_translation_budget -= 1
                if title_zh:
                    translated_count += 1

            importance = score_article(
                source=payload.source,
                event_type=event_type,
                asset_tag_count=asset_tag_count,
                published_at=payload.published_at,
                is_duplicate=is_duplicate,
            )
            article = {
                "id": article_id,
                "source": payload.source,
                "source_type": payload.source_type,
                "title": payload.title,
                "title_zh": title_zh,
                "summary": summary,
                "url": normalized_url,
                "published_at": payload.published_at,
                "fetched_at": payload.fetched_at,
                "language": payload.language,
                "raw_text": payload.raw_text,
                "clean_text": clean_body,
                "content_hash": content_hash,
                "importance_score": importance,
                "region": region,
                "sentiment": None,
                "event_type": event_type,
                "is_duplicate": int(is_duplicate),
                "duplicate_group_id": duplicate_group_id,
            }
            upsert_article(connection, article)
            replace_article_tags(
                connection,
                article_id,
                [{"tag_name": tag.tag_name, "tag_type": tag.tag_type, "score": tag.score} for tag in tags],
            )

            if event_assignment.event_key:
                now_iso = datetime.now(UTC).isoformat()
                topic = next((tag.tag_name for tag in tags if tag.tag_type == "topic"), None)
                asset_impact = ", ".join(sorted({tag.tag_name for tag in tags if tag.tag_type == "asset"})) or None
                event = {
                    "id": str(uuid4()),
                    "event_title": event_assignment.event_title or payload.title,
                    "event_summary": summary,
                    "first_seen_at": payload.published_at or now_iso,
                    "last_seen_at": payload.published_at or now_iso,
                    "importance_score": importance,
                    "status": "active",
                    "region": region,
                    "topic": topic,
                    "asset_impact": asset_impact,
                    "event_key": event_assignment.event_key,
                }
                event_id = upsert_event(connection, event)
                link_article_event(connection, article_id, event_id)

            stored_count += 1

        pruned_count = prune_articles(connection, settings.article_retention_count)

    return PipelineRunResult(
        status="success",
        message=(
            "Pipeline completed with live source ingestion."
            if translated_count == 0
            else f"Pipeline completed with live source ingestion and {translated_count} translated titles."
        ),
        collected_count=collected_count,
        stored_count=stored_count - pruned_count,
        duplicate_count=duplicate_count,
    )
