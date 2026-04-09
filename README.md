# Financial Intelligence Aggregation Dashboard MVP

This repository contains a Python + Streamlit MVP for a financial intelligence feedboard. The product goal is not to build a generic news site, but to create a research-oriented workflow for macro tracking, commodities research, market monitoring, and investment consulting.

## Current Status

The repository now includes a runnable MVP with:

- SQLite-backed core data model
- Alibaba Cloud Hong Kong ECS deployment path with `systemd`, `nginx`, scheduled ingestion, and daily SQLite backup
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
  - MktNews static JSON flash feed
- Minimal processing pipeline for:
  - text cleaning
  - URL, content, and lightweight story-key deduplication
  - rule-based tags
  - rule-based summary generation
  - minimal event grouping
  - rule-based importance scoring
- Optional title-only translation through a configurable OpenAI-compatible model endpoint, defaulting to Doubao Seed
- A Streamlit dashboard with a light paper-toned research board style, duplicate-story collapsing, improved search ranking, incremental history loading, and mobile-friendly collapsed controls

The project currently runs on the default local Python 3.14 environment.

## MVP Pipeline

The current pipeline is:

1. Collect articles from stable public sources
2. Normalize and clean text
3. Deduplicate by URL, content fingerprint, and lightweight story grouping
4. Infer tags from rule-based keyword matching
5. Generate a short summary
6. Optionally translate titles through a configurable translation model
7. Assign a minimal event grouping key
8. Compute rule-based importance score
9. Persist results to SQLite
10. Display the feed in Streamlit

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

The current dashboard defaults to a larger initial feed slice and supports incremental loading for deeper history browsing.

## Server Operations

Useful commands for the current Alibaba Cloud ECS deployment:

### Service Status

```bash
systemctl status news-dashboard --no-pager
```

查看网页服务状态，确认新闻终端页面是否正在运行。

```bash
systemctl status news-pipeline.timer --no-pager
```

查看定时抓取任务状态，确认自动更新是否仍在工作。

```bash
systemctl status news-pipeline.service --no-pager
```

查看最近一次抓取任务执行状态，适合排查为什么最近没有新消息。

```bash
systemctl status news-backup.timer --no-pager
```

查看数据库自动备份定时器状态，确认每天备份是否启用。

```bash
systemctl status news-backup.service --no-pager
```

查看最近一次数据库备份执行状态。

### Logs

```bash
journalctl -u news-dashboard -n 100 --no-pager
```

查看网页服务最近 100 行日志。页面打不开、启动失败、报错时优先看这个。

```bash
journalctl -u news-pipeline.service -n 100 --no-pager
```

查看抓取任务最近 100 行日志。适合排查新闻源抓取失败、翻译失败、数据库写入异常。

```bash
journalctl -u news-backup.service -n 50 --no-pager
```

查看数据库备份任务最近 50 行日志，确认备份是否真正执行成功。

### Restart And Stop

```bash
systemctl restart news-dashboard
```

重启网页服务。修改页面代码、样式或配置后常用。

```bash
systemctl restart news-pipeline.timer
```

重启定时抓取任务。修改抓取逻辑或定时器配置后使用。

```bash
systemctl stop news-dashboard
```

停止网页服务，适合临时下线页面。

```bash
systemctl start news-dashboard
```

启动网页服务。

### Manual Tasks

```bash
cd /root/global-market-news
source .venv/bin/activate
python scripts/run_pipeline.py
```

手动立即执行一轮抓取、清洗、翻译和入库，适合需要马上刷新数据时使用。

```bash
systemctl start news-backup.service
```

手动立即执行一次数据库备份。

### Timers And Backups

```bash
systemctl list-timers --all | grep news-pipeline
```

查看抓取定时任务的上次和下次执行时间。

```bash
systemctl list-timers --all | grep news-backup
```

查看备份定时任务的上次和下次执行时间。

```bash
ls -lh /root/backups/news
```

查看当前数据库备份文件列表和大小。

### Common Paths

```bash
cd /root/global-market-news
```

进入项目目录。

```bash
cd /root/backups/news
```

进入数据库备份目录。

### Edit Configuration

```bash
nano /root/global-market-news/.env
```

编辑环境变量配置，例如翻译 Key、自动更新参数和文章保留上限。

```bash
systemctl restart news-dashboard
systemctl restart news-pipeline.timer
```

修改 `.env` 后重启页面服务和定时抓取任务，让新配置生效。

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
- `TRANSLATION_API_KEY`
- `ARK_API_KEY`
- `DASHSCOPE_API_KEY` (legacy fallback)
- `TRANSLATION_MODEL`
- `TRANSLATION_BASE_URL`
- `TRANSLATION_SOURCE_LANG`
- `TRANSLATION_TARGET_LANG`
- `TRANSLATION_MAX_ITEMS_PER_RUN`
- `STORY_DEDUP_LOOKBACK_HOURS`

See [.env.example](C:\Users\hwsy5\Desktop\news\.env.example).

## Dashboard Capabilities

The current Streamlit board supports:

- light paper-toned research board layout
- source filter
- topic filter
- region filter
- search across titles, tags, and event titles
- title-prioritized search ranking, with summary matches treated as lower-priority hits
- sort by time or importance
- auto update toggle and interval control
- optional Chinese translated titles for foreign-language items
- summaries remain in the original source language
- important flash panel
- main feed timeline
- default initial feed load of 100 items with a `加载更多` interaction for deeper history browsing
- default duplicate-story collapsing in the main feed
- compact mobile-friendly control area with a collapsed filter panel
- source status side panel
- hot topic side panel

## Data Notes

- Default database: `data/news_mvp.db`
- SQLite is used for MVP speed and simplicity
- Schema is organized so a future PostgreSQL migration is manageable
- The pipeline can automatically prune the article table to the most recent retained records
- Duplicate stories are still stored in SQLite, but the main feed now collapses duplicate rows by default
- Each article is normalized to a single primary event mapping to avoid duplicate feed rows from repeated event joins
- SQLite connections use `WAL` mode and a busy timeout to reduce lock contention between the dashboard and scheduled ingestion
- The dashboard displays titles, summaries, tags, scores, and links rather than large raw article bodies

## What Is Implemented

- Federal Reserve official feed ingestion
- Reuters and BLS source-limited feed ingestion through Google News RSS search
- Bloomberg, CNBC, CNN, WSJ, FT, Yahoo Finance, Axios, and MktNews integrations
- Optional Doubao Seed title translation through Volcengine Ark's OpenAI-compatible endpoint
- Rule-based enrichment and lightweight duplicate-story collapsing
- Mobile-friendly collapsed controls and a refined light research-board UI
- Incremental feed loading for longer history browsing
- Search that prioritizes title matches and also supports tag and event lookups
- ECS deployment workflow with `systemd`, `nginx`, recurring pipeline runs, and SQLite backup

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
- Automatic translation is opt-in and depends on a configured translation API key
- The current translation mode only applies to titles; summaries remain in the source language
- Historical article retention defaults to the most recent 5000 records
- The dashboard does not render all retained rows at once; it loads history incrementally to keep Streamlit responsive
- Duplicate detection is heuristic and story grouping remains lightweight rather than entity-aware
- Event grouping is heuristic, not entity-aware
- Importance scoring is rule-based and intentionally simple
- Source status reflects observed article freshness, not full collector health telemetry

## Recommended Next Steps

- Improve event clustering quality
- Make source status reflect real collector success/failure
- Add more research-oriented panels such as event view and topic drill-down
- Improve scoring logic with stronger source, recency, and asset impact rules
