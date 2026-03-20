from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from news_mvp.config import Settings
from news_mvp.db import connection_scope, fetch_scalar

HIDDEN_SOURCES = ("联合早报",)


@dataclass(slots=True)
class DashboardStats:
    article_count: int
    event_count: int
    tag_count: int


@dataclass(slots=True)
class ArticleCard:
    id: str
    title: str
    title_zh: str | None
    summary_zh: str | None
    source: str
    published_at: str | None
    fetched_at: str
    region: str | None
    event_type: str | None
    summary: str | None
    url: str
    importance_score: float
    is_duplicate: int
    dedup_reason: str | None
    event_title: str | None
    event_title_zh: str | None
    topic_tags: list[str]
    asset_tags: list[str]


@dataclass(slots=True)
class SourceStatus:
    source: str
    article_count: int
    latest_published_at: str | None
    status: str


@dataclass(slots=True)
class TopicPulse:
    topic_name: str
    article_count: int


@dataclass(slots=True)
class FlashItem:
    title: str
    title_zh: str | None
    source: str
    url: str
    importance_score: float


def _hidden_source_placeholders() -> str:
    return ", ".join("?" for _ in HIDDEN_SOURCES)


def _append_hidden_source_filter(query: str, table_alias: str = "") -> str:
    prefix = f"{table_alias}." if table_alias else ""
    return query + f" AND {prefix}source NOT IN ({_hidden_source_placeholders()})"


def load_dashboard_stats(settings: Settings) -> DashboardStats:
    with connection_scope(settings) as connection:
        article_count = int(
            connection.execute(
                f"SELECT COUNT(*) FROM articles WHERE source NOT IN ({_hidden_source_placeholders()})",
                HIDDEN_SOURCES,
            ).fetchone()[0]
            or 0
        )
    return DashboardStats(
        article_count=article_count,
        event_count=fetch_scalar(settings, "SELECT COUNT(*) FROM events"),
        tag_count=fetch_scalar(settings, "SELECT COUNT(*) FROM tags"),
    )


def load_filter_options(settings: Settings) -> dict[str, list[str]]:
    with connection_scope(settings) as connection:
        rows = connection.execute(
            f"""
            SELECT 'source' AS tag_type, source AS tag_name
            FROM articles
            WHERE source NOT IN ({_hidden_source_placeholders()})
            GROUP BY source
            UNION ALL
            SELECT DISTINCT tag_type, tag_name
            FROM tags
            WHERE tag_type IN ('topic', 'region')
            ORDER BY tag_type, tag_name
            """,
            HIDDEN_SOURCES,
        ).fetchall()
    options = {"topic": [], "region": [], "source": []}
    for row in rows:
        options[row["tag_type"]].append(row["tag_name"])
    return options


def load_article_feed(
    settings: Settings,
    hours: int,
    topic: str | None = None,
    region: str | None = None,
    source: str | None = None,
    search: str | None = None,
    sort_by: str = "importance",
    limit: int | None = None,
    collapse_duplicates: bool = True,
) -> list[ArticleCard]:
    lookback_floor = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
    params: list[Any] = [lookback_floor]
    search_rank_sql = "999"
    query = """
        SELECT
            a.id,
            a.title,
            a.title_zh,
            a.summary_zh,
            a.source,
            a.published_at,
            a.fetched_at,
            a.region,
            a.event_type,
            a.summary,
            a.url,
            a.importance_score,
            a.is_duplicate,
            a.dedup_reason,
            """ + search_rank_sql + """ AS search_rank,
            (
                SELECT e.event_title
                FROM article_event_map aem
                JOIN events e ON aem.event_id = e.id
                WHERE aem.article_id = a.id
                ORDER BY e.importance_score DESC, e.last_seen_at DESC, e.first_seen_at DESC, e.id DESC
                LIMIT 1
            ) AS event_title,
            (
                SELECT e.event_title_zh
                FROM article_event_map aem
                JOIN events e ON aem.event_id = e.id
                WHERE aem.article_id = a.id
                ORDER BY e.importance_score DESC, e.last_seen_at DESC, e.first_seen_at DESC, e.id DESC
                LIMIT 1
            ) AS event_title_zh,
            (
                SELECT GROUP_CONCAT(DISTINCT t.tag_name)
                FROM article_tags at
                JOIN tags t ON at.tag_id = t.id
                WHERE at.article_id = a.id
                  AND t.tag_type = 'topic'
            ) AS topic_tags,
            (
                SELECT GROUP_CONCAT(DISTINCT t.tag_name)
                FROM article_tags at
                JOIN tags t ON at.tag_id = t.id
                WHERE at.article_id = a.id
                  AND t.tag_type = 'asset'
            ) AS asset_tags
        FROM articles a
        WHERE COALESCE(a.published_at, a.fetched_at) >= ?
    """
    query = _append_hidden_source_filter(query, "a")
    params.extend(HIDDEN_SOURCES)
    if collapse_duplicates:
        query += " AND (a.is_duplicate = 0 OR COALESCE(a.canonical_article_id, a.id) = a.id)"
    if region:
        query += " AND a.region = ?"
        params.append(region)
    if source:
        query += " AND a.source = ?"
        params.append(source)
    if topic:
        query += """
            AND EXISTS (
                SELECT 1
                FROM article_tags at2
                JOIN tags t2 ON at2.tag_id = t2.id
                WHERE at2.article_id = a.id
                  AND t2.tag_type = 'topic'
                  AND t2.tag_name = ?
            )
        """
        params.append(topic)
    if search:
        normalized_search = search.strip().lower()
        keyword = f"%{normalized_search}%"
        search_rank_sql = """
            CASE
                WHEN LOWER(a.title) = ? OR LOWER(COALESCE(a.title_zh, '')) = ? THEN 0
                WHEN LOWER(a.title) LIKE ? OR LOWER(COALESCE(a.title_zh, '')) LIKE ? THEN 1
                WHEN EXISTS (
                    SELECT 1
                    FROM article_tags at_search
                    JOIN tags t_search ON at_search.tag_id = t_search.id
                    WHERE at_search.article_id = a.id
                      AND LOWER(t_search.tag_name) LIKE ?
                ) THEN 2
                WHEN EXISTS (
                    SELECT 1
                    FROM article_event_map aem_search
                    JOIN events e_search ON aem_search.event_id = e_search.id
                    WHERE aem_search.article_id = a.id
                      AND (
                          LOWER(COALESCE(e_search.event_title, '')) LIKE ?
                          OR LOWER(COALESCE(e_search.event_title_zh, '')) LIKE ?
                      )
                ) THEN 3
                WHEN LOWER(COALESCE(a.summary, '')) LIKE ? OR LOWER(COALESCE(a.summary_zh, '')) LIKE ? THEN 4
                ELSE 999
            END
        """
        query = query.replace("999 AS search_rank", f"{search_rank_sql} AS search_rank")
        query += """
            AND (
                LOWER(a.title) LIKE ?
                OR LOWER(COALESCE(a.title_zh, '')) LIKE ?
                OR LOWER(COALESCE(a.summary, '')) LIKE ?
                OR LOWER(COALESCE(a.summary_zh, '')) LIKE ?
                OR EXISTS (
                    SELECT 1
                    FROM article_tags at_search
                    JOIN tags t_search ON at_search.tag_id = t_search.id
                    WHERE at_search.article_id = a.id
                      AND LOWER(t_search.tag_name) LIKE ?
                )
                OR EXISTS (
                    SELECT 1
                    FROM article_event_map aem_search
                    JOIN events e_search ON aem_search.event_id = e_search.id
                    WHERE aem_search.article_id = a.id
                      AND (
                          LOWER(COALESCE(e_search.event_title, '')) LIKE ?
                          OR LOWER(COALESCE(e_search.event_title_zh, '')) LIKE ?
                      )
                )
            )
        """
        params.extend(
            [
                normalized_search,
                normalized_search,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
            ]
        )
    if search:
        if sort_by == "time":
            query += " ORDER BY search_rank ASC, COALESCE(a.published_at, a.fetched_at) DESC, a.importance_score DESC"
        else:
            query += " ORDER BY search_rank ASC, a.importance_score DESC, COALESCE(a.published_at, a.fetched_at) DESC"
    elif sort_by == "time":
        query += " ORDER BY COALESCE(a.published_at, a.fetched_at) DESC, a.importance_score DESC"
    else:
        query += " ORDER BY a.importance_score DESC, COALESCE(a.published_at, a.fetched_at) DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    with connection_scope(settings) as connection:
        rows = connection.execute(query, params).fetchall()

    def split_tags(value: str | None) -> list[str]:
        if not value:
            return []
        return [tag for tag in value.split(",") if tag]

    return [
        ArticleCard(
            id=row["id"],
            title=row["title"],
            title_zh=row["title_zh"],
            summary_zh=row["summary_zh"],
            source=row["source"],
            published_at=row["published_at"],
            fetched_at=row["fetched_at"],
            region=row["region"],
            event_type=row["event_type"],
            summary=row["summary"],
            url=row["url"],
            importance_score=float(row["importance_score"] or 0),
            is_duplicate=int(row["is_duplicate"] or 0),
            dedup_reason=row["dedup_reason"],
            event_title=row["event_title"],
            event_title_zh=row["event_title_zh"],
            topic_tags=split_tags(row["topic_tags"]),
            asset_tags=split_tags(row["asset_tags"]),
        )
        for row in rows
    ]


def load_source_status(settings: Settings, hours: int) -> list[SourceStatus]:
    lookback_floor = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
    params: list[Any] = [lookback_floor, *HIDDEN_SOURCES]
    with connection_scope(settings) as connection:
        rows = connection.execute(
            f"""
            SELECT
                source,
                COUNT(*) AS article_count,
                MAX(COALESCE(published_at, fetched_at)) AS latest_published_at
            FROM articles
            WHERE COALESCE(published_at, fetched_at) >= ?
              AND source NOT IN ({_hidden_source_placeholders()})
            GROUP BY source
            ORDER BY article_count DESC, source ASC
            """,
            params,
        ).fetchall()
    return [
        SourceStatus(
            source=row["source"],
            article_count=int(row["article_count"] or 0),
            latest_published_at=row["latest_published_at"],
            status=_derive_source_status(row["latest_published_at"], hours, int(row["article_count"] or 0)),
        )
        for row in rows
    ]


def load_topic_pulse(settings: Settings, hours: int, limit: int = 8) -> list[TopicPulse]:
    lookback_floor = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
    params: list[Any] = [lookback_floor, *HIDDEN_SOURCES, limit]
    with connection_scope(settings) as connection:
        rows = connection.execute(
            f"""
            SELECT
                t.tag_name AS topic_name,
                COUNT(*) AS article_count
            FROM article_tags at
            JOIN tags t ON at.tag_id = t.id
            JOIN articles a ON at.article_id = a.id
            WHERE t.tag_type = 'topic'
              AND COALESCE(a.published_at, a.fetched_at) >= ?
              AND a.source NOT IN ({_hidden_source_placeholders()})
            GROUP BY t.tag_name
            ORDER BY article_count DESC, t.tag_name ASC
            LIMIT ?
            """,
            params,
        ).fetchall()
    return [
        TopicPulse(topic_name=row["topic_name"], article_count=int(row["article_count"] or 0))
        for row in rows
    ]


def load_flash_items(settings: Settings, hours: int, limit: int = 5) -> list[FlashItem]:
    rows = load_article_feed(settings, hours=hours, sort_by="importance", limit=limit * 2)
    unique_rows: list[ArticleCard] = []
    seen_titles: set[str] = set()
    for row in rows:
        key = row.title.strip().lower()
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique_rows.append(row)
        if len(unique_rows) >= limit:
            break
    return [
        FlashItem(
            title=row.title,
            title_zh=row.title_zh,
            source=row.source,
            url=row.url,
            importance_score=row.importance_score,
        )
        for row in unique_rows
    ]


def _derive_source_status(latest_published_at: str | None, hours: int, article_count: int) -> str:
    if article_count <= 0 or not latest_published_at:
        return "idle"
    try:
        latest_dt = datetime.fromisoformat(latest_published_at.replace("Z", "+00:00"))
        age_hours = (datetime.now(UTC) - latest_dt.astimezone(UTC)).total_seconds() / 3600
    except ValueError:
        return "idle"
    if age_hours <= max(6, hours / 8):
        return "online"
    if age_hours <= hours:
        return "lagging"
    return "idle"
