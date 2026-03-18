from __future__ import annotations


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        source_type TEXT NOT NULL,
        title TEXT NOT NULL,
        title_zh TEXT,
        summary TEXT,
        url TEXT NOT NULL UNIQUE,
        published_at TEXT,
        fetched_at TEXT NOT NULL,
        language TEXT NOT NULL DEFAULT 'en',
        raw_text TEXT,
        clean_text TEXT,
        content_hash TEXT,
        importance_score REAL NOT NULL DEFAULT 0,
        region TEXT,
        sentiment TEXT,
        event_type TEXT,
        is_duplicate INTEGER NOT NULL DEFAULT 0,
        duplicate_group_id TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tags (
        id TEXT PRIMARY KEY,
        tag_name TEXT NOT NULL UNIQUE,
        tag_type TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS article_tags (
        article_id TEXT NOT NULL,
        tag_id TEXT NOT NULL,
        score REAL NOT NULL DEFAULT 0,
        PRIMARY KEY (article_id, tag_id),
        FOREIGN KEY (article_id) REFERENCES articles (id),
        FOREIGN KEY (tag_id) REFERENCES tags (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        event_title TEXT NOT NULL,
        event_summary TEXT,
        first_seen_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        importance_score REAL NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'active',
        region TEXT,
        topic TEXT,
        asset_impact TEXT,
        event_key TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS article_event_map (
        article_id TEXT NOT NULL,
        event_id TEXT NOT NULL,
        PRIMARY KEY (article_id, event_id),
        FOREIGN KEY (article_id) REFERENCES articles (id),
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_articles_published_at
    ON articles (published_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_articles_importance_score
    ON articles (importance_score DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_articles_duplicate_group
    ON articles (duplicate_group_id)
    """,
]


DEFAULT_TAG_SEEDS = [
    ("topic_macro", "macro", "topic"),
    ("topic_central_bank", "central_bank", "topic"),
    ("topic_inflation", "inflation", "topic"),
    ("topic_commodities", "commodities", "topic"),
    ("topic_equities", "equities", "topic"),
    ("topic_bonds", "bonds", "topic"),
    ("topic_fx", "fx", "topic"),
    ("topic_geopolitics", "geopolitics", "topic"),
    ("asset_usd", "USD", "asset"),
    ("asset_treasury", "UST", "asset"),
    ("asset_gold", "gold", "asset"),
    ("asset_oil", "oil", "asset"),
    ("asset_a_share", "A_share", "asset"),
    ("asset_ferrous", "ferrous_chain", "asset"),
    ("region_us", "United States", "region"),
    ("region_cn", "China", "region"),
    ("region_eu", "Europe", "region"),
    ("region_global", "Global", "region"),
    ("event_data", "data", "event_type"),
    ("event_policy", "policy", "event_type"),
    ("event_breaking", "breaking", "event_type"),
    ("event_earnings", "earnings", "event_type"),
    ("event_geopolitics", "geopolitics", "event_type"),
    ("event_regulation", "regulation", "event_type"),
]
