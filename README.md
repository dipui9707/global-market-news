# Financial Intelligence Aggregation Dashboard MVP

This repository contains a Python + Streamlit MVP for a financial intelligence feedboard. The product goal is not to build a generic news site, but to create a high-density research and advisory workflow for macro tracking, commodities research, market monitoring, and investment consulting.

## Current Status

The repository now includes a runnable MVP with:

- SQLite-backed core data model
- Live source ingestion from:
  - Federal Reserve official RSS
  - Reuters via Google News RSS source search
  - BLS via Google News RSS source search
  - Bloomberg RSS
  - CNBC RSS
  - CNN RSS
  - WSJ RSS
  - FT RSS
  - Yahoo Finance RSS
  - Axios RSS
  - SCMP RSS
  - MktNews static JSON flash feed
- Minimal processing pipeline for:
  - text cleaning
  - URL and content fingerprint deduplication
  - rule-based tags
  - rule-based summary generation
  - minimal event grouping
  - rule-based importance scoring
- A Streamlit dashboard styled as a terminal-like financial information board

An optional Qwen-MT title-translation path is available through Alibaba Cloud Model Studio. The project currently runs on the default local Python 3.14 environment.

## MVP Pipeline

The current pipeline is:

1. Collect articles from stable public sources
2. Normalize and clean text
3. Deduplicate by URL and content fingerprint
4. Infer tags from rule-based keyword matching
5. Generate a short summary
6. Assign a minimal event grouping key
7. Compute rule-based importance score
8. Persist results to SQLite
9. Display the feed in Streamlit

## Project Structure

```text
news/
├─ data/
├─ scripts/
│  ├─ init_db.py
│  └─ run_pipeline.py
├─ src/
│  └─ news_mvp/
│     ├─ collectors/
│     ├─ dashboard/
│     │  ├─ components.py
│     │  ├─ queries.py
│     │  ├─ styles.py
│     │  └─ ui.py
│     ├─ pipeline/
│     ├─ config.py
│     ├─ db.py
│     └─ schema.py
├─ .env.example
├─ AGENTS.md
├─ PLANS.md
├─ pyproject.toml
└─ streamlit_app.py
```

## Setup

1. Create and activate a virtual environment.
2. Install the project in editable mode:

```bash
python -m pip install -e .
```

3. Create an environment file:

```bash
copy .env.example .env
```

4. Initialize the database:

```bash
python scripts/init_db.py
```

## Run

Fetch the latest data, then start the dashboard:

```bash
python scripts/run_pipeline.py
streamlit run streamlit_app.py
```

The dashboard also includes a built-in refresh button for rerunning ingestion from the UI.

## Configuration

Current environment variables:

- `APP_ENV`
- `DATABASE_URL`
- `STREAMLIT_SERVER_PORT`
- `DEFAULT_LOOKBACK_HOURS`
- `DEFAULT_PAGE_SIZE`
- `COLLECTOR_ITEM_LIMIT`
- `ARTICLE_RETENTION_COUNT`
- `AUTO_UPDATE_ENABLED`
- `AUTO_UPDATE_INTERVAL_SECONDS`
- `TRANSLATION_ENABLED`
- `DASHSCOPE_API_KEY`
- `TRANSLATION_MODEL`
- `TRANSLATION_BASE_URL`
- `TRANSLATION_SOURCE_LANG`
- `TRANSLATION_TARGET_LANG`
- `TRANSLATION_MAX_ITEMS_PER_RUN`

See [.env.example](C:\Users\hwsy5\Desktop\news\.env.example).

## Dashboard Capabilities

The current Streamlit board supports:

- terminal-style dark theme layout
- source filter
- topic filter
- region filter
- search
- sort by time or importance
- auto update toggle and interval control
- optional Chinese translated titles for foreign-language items
- important flash panel
- main feed timeline
- source status side panel
- hot topic side panel

## Data Notes

- Default database: `data/news_mvp.db`
- SQLite is used for MVP speed and simplicity
- Schema is organized so a future PostgreSQL migration is manageable
- The pipeline can automatically prune the article table to the most recent retained records
- The dashboard displays metadata, summaries, tags, scores, and event grouping rather than large raw article bodies

## What Is Implemented

- Federal Reserve official feed ingestion
- Reuters and BLS source-limited feed ingestion through Google News RSS search
- Bloomberg, CNBC, CNN, WSJ, FT, Yahoo Finance, Axios, SCMP, and MktNews integrations
- Optional Alibaba Cloud Qwen-MT title translation
- Rule-based enrichment pipeline
- Terminal-style research feedboard

## What Is Not Implemented Yet

- Direct Reuters site parsing
- Direct BLS source feed parsing in the current environment
- Strong cross-source event clustering
- Real sentiment analysis
- Production scheduling and monitoring
- Historical backfill workflows
- User management or multi-tenant features

## Known Limitations

- Reuters and BLS currently depend on Google News RSS as a transport layer
- Some third-party publisher RSS feeds may change structure or rate-limit intermittently
- Automatic translation is opt-in and depends on a configured DashScope API key
- Historical article retention defaults to the most recent 5000 records
- Deduplication is still minimal
- Event grouping is heuristic, not entity-aware
- Importance scoring is rule-based and intentionally simple
- Source status reflects observed article freshness, not full collector health telemetry

## Recommended Next Steps

- Improve event clustering quality
- Make source status reflect real collector success/failure
- Add more research-oriented panels such as event view and topic drill-down
- Improve scoring logic with stronger source, recency, and asset impact rules
