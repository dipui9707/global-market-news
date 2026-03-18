from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from news_mvp.config import Settings
from news_mvp.schema import DEFAULT_TAG_SEEDS, SCHEMA_STATEMENTS


def ensure_database_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(settings: Settings) -> sqlite3.Connection:
    database_path = settings.database_path
    ensure_database_parent(database_path)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def connection_scope(settings: Settings) -> Iterator[sqlite3.Connection]:
    connection = get_connection(settings)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database(settings: Settings) -> None:
    with connection_scope(settings) as connection:
        cursor = connection.cursor()
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
        cursor.executemany(
            """
            INSERT OR IGNORE INTO tags (id, tag_name, tag_type)
            VALUES (?, ?, ?)
            """,
            DEFAULT_TAG_SEEDS,
        )


def fetch_scalar(settings: Settings, query: str) -> int:
    with connection_scope(settings) as connection:
        row = connection.execute(query).fetchone()
        return int(row[0]) if row and row[0] is not None else 0


def fetch_article_by_url(connection: sqlite3.Connection, url: str) -> sqlite3.Row | None:
    return connection.execute("SELECT * FROM articles WHERE url = ?", (url,)).fetchone()


def fetch_article_by_content_hash(connection: sqlite3.Connection, content_hash: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM articles WHERE content_hash = ? ORDER BY fetched_at ASC LIMIT 1",
        (content_hash,),
    ).fetchone()


def upsert_article(connection: sqlite3.Connection, article: dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO articles (
            id, source, source_type, title, title_zh, summary, url, published_at,
            fetched_at, language, raw_text, clean_text, content_hash, importance_score,
            region, sentiment, event_type, is_duplicate, duplicate_group_id
        ) VALUES (
            :id, :source, :source_type, :title, :title_zh, :summary, :url, :published_at,
            :fetched_at, :language, :raw_text, :clean_text, :content_hash, :importance_score,
            :region, :sentiment, :event_type, :is_duplicate, :duplicate_group_id
        )
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            title_zh = excluded.title_zh,
            summary = excluded.summary,
            published_at = excluded.published_at,
            fetched_at = excluded.fetched_at,
            raw_text = excluded.raw_text,
            clean_text = excluded.clean_text,
            content_hash = excluded.content_hash,
            importance_score = excluded.importance_score,
            region = excluded.region,
            event_type = excluded.event_type,
            is_duplicate = excluded.is_duplicate,
            duplicate_group_id = excluded.duplicate_group_id
        """,
        article,
    )


def update_article_translation(connection: sqlite3.Connection, article_id: str, title_zh: str) -> None:
    connection.execute(
        """
        UPDATE articles
        SET title_zh = ?
        WHERE id = ?
        """,
        (title_zh, article_id),
    )


def prune_articles(connection: sqlite3.Connection, keep_count: int) -> int:
    if keep_count <= 0:
        return 0

    rows = connection.execute(
        """
        SELECT id
        FROM articles
        ORDER BY COALESCE(published_at, fetched_at) DESC, fetched_at DESC, id DESC
        LIMIT -1 OFFSET ?
        """,
        (keep_count,),
    ).fetchall()
    article_ids = [row["id"] for row in rows]
    if not article_ids:
        return 0

    placeholders = ", ".join("?" for _ in article_ids)
    connection.execute(f"DELETE FROM article_tags WHERE article_id IN ({placeholders})", article_ids)
    connection.execute(f"DELETE FROM article_event_map WHERE article_id IN ({placeholders})", article_ids)
    connection.execute(f"DELETE FROM articles WHERE id IN ({placeholders})", article_ids)

    connection.execute(
        """
        DELETE FROM events
        WHERE id NOT IN (
            SELECT DISTINCT event_id
            FROM article_event_map
        )
        """
    )

    connection.execute(
        """
        DELETE FROM tags
        WHERE id NOT IN (
            SELECT DISTINCT tag_id
            FROM article_tags
        )
          AND id NOT IN (
            SELECT id
            FROM tags
            WHERE id IN (
                'topic_macro', 'topic_central_bank', 'topic_inflation', 'topic_commodities',
                'topic_equities', 'topic_bonds', 'topic_fx', 'topic_geopolitics',
                'asset_usd', 'asset_treasury', 'asset_gold', 'asset_oil', 'asset_a_share',
                'asset_ferrous', 'region_us', 'region_cn', 'region_eu', 'region_global',
                'event_data', 'event_policy', 'event_breaking', 'event_earnings',
                'event_geopolitics', 'event_regulation'
            )
        )
        """
    )

    return len(article_ids)


def replace_article_tags(connection: sqlite3.Connection, article_id: str, tags: list[dict[str, Any]]) -> None:
    connection.execute("DELETE FROM article_tags WHERE article_id = ?", (article_id,))
    for tag in tags:
        row = connection.execute(
            "SELECT id FROM tags WHERE tag_name = ? AND tag_type = ?",
            (tag["tag_name"], tag["tag_type"]),
        ).fetchone()
        if row is None:
            continue
        connection.execute(
            """
            INSERT OR REPLACE INTO article_tags (article_id, tag_id, score)
            VALUES (?, ?, ?)
            """,
            (article_id, row["id"], tag["score"]),
        )


def upsert_event(connection: sqlite3.Connection, event: dict[str, Any]) -> str:
    existing = connection.execute("SELECT id FROM events WHERE event_key = ?", (event["event_key"],)).fetchone()
    if existing:
        event["id"] = existing["id"]
    connection.execute(
        """
        INSERT INTO events (
            id, event_title, event_summary, first_seen_at, last_seen_at,
            importance_score, status, region, topic, asset_impact, event_key
        ) VALUES (
            :id, :event_title, :event_summary, :first_seen_at, :last_seen_at,
            :importance_score, :status, :region, :topic, :asset_impact, :event_key
        )
        ON CONFLICT(id) DO UPDATE SET
            event_title = excluded.event_title,
            event_summary = excluded.event_summary,
            last_seen_at = excluded.last_seen_at,
            importance_score = CASE
                WHEN excluded.importance_score > events.importance_score THEN excluded.importance_score
                ELSE events.importance_score
            END,
            region = COALESCE(excluded.region, events.region),
            topic = COALESCE(excluded.topic, events.topic),
            asset_impact = COALESCE(excluded.asset_impact, events.asset_impact)
        """,
        event,
    )
    return event["id"]


def link_article_event(connection: sqlite3.Connection, article_id: str, event_id: str) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO article_event_map (article_id, event_id)
        VALUES (?, ?)
        """,
        (article_id, event_id),
    )
