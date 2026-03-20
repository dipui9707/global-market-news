from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
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
        for statement in SCHEMA_STATEMENTS[:5]:
            cursor.execute(statement)
        _ensure_article_schema(connection)
        _ensure_event_schema(connection)
        _normalize_article_event_map(connection)
        for statement in SCHEMA_STATEMENTS[5:]:
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


def fetch_article_by_story_key(
    connection: sqlite3.Connection,
    story_key: str,
    reference_time: str | None,
    lookback_hours: int,
    exclude_article_id: str | None = None,
) -> sqlite3.Row | None:
    lookback_anchor = _coerce_iso_datetime(reference_time) or datetime.now(UTC)
    lookback_floor = (lookback_anchor - timedelta(hours=lookback_hours)).isoformat()
    query = """
        SELECT *
        FROM articles
        WHERE story_key = ?
          AND COALESCE(published_at, fetched_at) >= ?
    """
    params: list[Any] = [story_key, lookback_floor]
    if exclude_article_id:
        query += " AND id != ?"
        params.append(exclude_article_id)
    query += """
        ORDER BY
            CASE WHEN canonical_article_id IS NULL OR canonical_article_id = id THEN 0 ELSE 1 END,
            importance_score DESC,
            COALESCE(published_at, fetched_at) DESC,
            fetched_at DESC
        LIMIT 1
    """
    return connection.execute(query, params).fetchone()


def fetch_event_by_key(connection: sqlite3.Connection, event_key: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM events WHERE event_key = ?",
        (event_key,),
    ).fetchone()


def upsert_article(connection: sqlite3.Connection, article: dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO articles (
            id, source, source_type, title, title_zh, summary, summary_zh, url, published_at,
            fetched_at, language, raw_text, clean_text, content_hash, story_key,
            importance_score, region, sentiment, event_type, is_duplicate,
            duplicate_group_id, dedup_reason, canonical_article_id
        ) VALUES (
            :id, :source, :source_type, :title, :title_zh, :summary, :summary_zh, :url, :published_at,
            :fetched_at, :language, :raw_text, :clean_text, :content_hash, :story_key,
            :importance_score, :region, :sentiment, :event_type, :is_duplicate,
            :duplicate_group_id, :dedup_reason, :canonical_article_id
        )
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            title_zh = excluded.title_zh,
            summary = excluded.summary,
            summary_zh = excluded.summary_zh,
            published_at = excluded.published_at,
            fetched_at = excluded.fetched_at,
            raw_text = excluded.raw_text,
            clean_text = excluded.clean_text,
            content_hash = excluded.content_hash,
            story_key = excluded.story_key,
            importance_score = excluded.importance_score,
            region = excluded.region,
            event_type = excluded.event_type,
            is_duplicate = excluded.is_duplicate,
            duplicate_group_id = excluded.duplicate_group_id,
            dedup_reason = excluded.dedup_reason,
            canonical_article_id = excluded.canonical_article_id
        """,
        article,
    )


def update_article_translations(
    connection: sqlite3.Connection,
    article_id: str,
    *,
    title_zh: str | None = None,
    summary_zh: str | None = None,
) -> None:
    updates: list[str] = []
    params: list[Any] = []
    if title_zh is not None:
        updates.append("title_zh = ?")
        params.append(title_zh)
    if summary_zh is not None:
        updates.append("summary_zh = ?")
        params.append(summary_zh)
    if not updates:
        return
    params.append(article_id)
    connection.execute(
        f"""
        UPDATE articles
        SET {", ".join(updates)}
        WHERE id = ?
        """,
        params,
    )


def update_event_translation(connection: sqlite3.Connection, event_id: str, event_title_zh: str) -> None:
    connection.execute(
        """
        UPDATE events
        SET event_title_zh = ?
        WHERE id = ?
        """,
        (event_title_zh, event_id),
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
            id, event_title, event_title_zh, event_summary, first_seen_at, last_seen_at,
            importance_score, status, region, topic, asset_impact, event_key
        ) VALUES (
            :id, :event_title, :event_title_zh, :event_summary, :first_seen_at, :last_seen_at,
            :importance_score, :status, :region, :topic, :asset_impact, :event_key
        )
        ON CONFLICT(id) DO UPDATE SET
            event_title = excluded.event_title,
            event_title_zh = COALESCE(excluded.event_title_zh, events.event_title_zh),
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
        DELETE FROM article_event_map
        WHERE article_id = ?
          AND event_id != ?
        """,
        (article_id, event_id),
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO article_event_map (article_id, event_id)
        VALUES (?, ?)
        """,
        (article_id, event_id),
    )


def _ensure_article_schema(connection: sqlite3.Connection) -> None:
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(articles)").fetchall()
    }
    required_columns = {
        "summary_zh": "TEXT",
        "story_key": "TEXT",
        "dedup_reason": "TEXT",
        "canonical_article_id": "TEXT",
    }
    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            connection.execute(f"ALTER TABLE articles ADD COLUMN {column_name} {column_type}")

    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_articles_story_key ON articles (story_key)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_articles_canonical_article ON articles (canonical_article_id)"
    )


def _ensure_event_schema(connection: sqlite3.Connection) -> None:
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(events)").fetchall()
    }
    if "event_title_zh" not in existing_columns:
        connection.execute("ALTER TABLE events ADD COLUMN event_title_zh TEXT")


def _normalize_article_event_map(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT
            aem.article_id,
            aem.event_id,
            COALESCE(e.importance_score, 0) AS importance_score,
            COALESCE(e.last_seen_at, '') AS last_seen_at,
            COALESCE(e.first_seen_at, '') AS first_seen_at
        FROM article_event_map aem
        LEFT JOIN events e ON aem.event_id = e.id
        ORDER BY
            aem.article_id ASC,
            importance_score DESC,
            last_seen_at DESC,
            first_seen_at DESC,
            aem.event_id DESC
        """
    ).fetchall()

    keep_by_article: dict[str, str] = {}
    stale_rows: list[tuple[str, str]] = []
    for row in rows:
        article_id = row["article_id"]
        event_id = row["event_id"]
        if article_id not in keep_by_article:
            keep_by_article[article_id] = event_id
            continue
        stale_rows.append((article_id, event_id))

    for article_id, event_id in stale_rows:
        connection.execute(
            """
            DELETE FROM article_event_map
            WHERE article_id = ?
              AND event_id = ?
            """,
            (article_id, event_id),
        )

    connection.execute(
        """
        DELETE FROM events
        WHERE id NOT IN (
            SELECT DISTINCT event_id
            FROM article_event_map
        )
        """
    )


def _coerce_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None
