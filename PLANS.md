# MVP Plan

## Stage 1: Foundation And Skeleton

Status: completed

Delivered:

- Python project scaffold
- SQLite schema and DB initialization
- Collector and pipeline module structure
- Initial Streamlit app shell
- Base project documentation

Validation completed:

- `python scripts/init_db.py`
- `streamlit run streamlit_app.py`

## Stage 2: Initial Source Integrations

Status: completed

Delivered:

- Federal Reserve official RSS collector
- Reuters collector via Google News RSS source search
- BLS collector via Google News RSS source search
- Multi-source media collector expansion for Bloomberg, CNBC, CNN, WSJ, FT, Yahoo Finance, Axios, SCMP, and MktNews
- Pipeline orchestration entrypoint
- Article persistence into SQLite

Validation completed:

- `python scripts/run_pipeline.py`
- Live article records persisted to `articles`

## Stage 3: Enrichment And Feedboard MVP

Status: completed

Delivered:

- Rule-based cleaning
- URL and content fingerprint deduplication
- Rule-based tagging
- Rule-based summarization
- Minimal event grouping
- Rule-based importance scoring
- Main feedboard UI with filters and side panels
- Optional in-dashboard auto-update with timed pipeline refresh

Validation completed:

- Dashboard shows feed items with tags, summary, importance, and event grouping
- Sorting, filtering, and refresh are available in the UI

## Stage 4: Dashboard Visual Refinement

Status: completed

Delivered:

- Terminal-style dark dashboard layout
- Header and control area redesign
- Flash panel and timeline-style feed presentation
- Source status side panel
- Hot topic side panel
- Multiple refinement passes on spacing, control alignment, and visual density

Validation completed:

- Streamlit UI reachable at local dashboard address
- Layout supports current MVP data and filters

## Translation Experiment

Status: rolled back

Summary:

- Earlier translation experiments were rolled back
- The current baseline now supports an optional Alibaba Cloud Qwen-MT title translation path
- Translation remains opt-in so the core ingestion pipeline stays runnable without model credentials

## Current Baseline

The repository currently represents:

- Python 3.14 local runtime
- SQLite-backed MVP
- Live ingestion from official macro sources plus a wider financial media set
- Rule-based enrichment pipeline
- A terminal-style financial information board focused on latest-feed workflow
- Automatic retention cap for the article table to keep the SQLite dataset bounded

## Next Suggested Work

- Improve event clustering across sources
- Make source status reflect real collector success/failure
- Add event-centric and topic-centric research views
- Harden source adapters and feed quality
- Improve importance scoring and dashboard drill-down behavior
