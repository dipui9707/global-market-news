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
- Multi-source media collector expansion for Bloomberg, CNBC, CNN, WSJ, FT, Yahoo Finance, Axios, and MktNews
- Pipeline orchestration entrypoint
- Article persistence into SQLite

Validation completed:

- `python scripts/run_pipeline.py`
- Live article records persisted to `articles`

## Stage 3: Enrichment And Feedboard MVP

Status: completed

Delivered:

- Rule-based cleaning
- URL, content fingerprint, and lightweight story-key deduplication
- Rule-based tagging
- Rule-based summarization
- Optional title-only translation through a configurable OpenAI-compatible translation endpoint
- Minimal event grouping
- Rule-based importance scoring
- Main feedboard UI with filters and side panels
- Search ranking that prioritizes title matches and supports tag/event lookup
- Optional in-dashboard auto-update with timed pipeline refresh
- Main feed duplicate-story collapsing so repeated coverage does not flood the board
- Query-side and DB-side normalization to keep each article mapped to a single primary event
- Incremental feed loading for longer history browsing

Validation completed:

- Dashboard shows feed items with tags, summary, importance, and event grouping
- Sorting, filtering, and refresh are available in the UI

## Stage 4: Dashboard Visual Refinement (Early Light Theme)

Status: completed (superseded by Stage 6 dark theme)

Delivered:

- Light paper-toned dashboard layout (replaced by the dark premium theme in Stage 6)
- Header and control area redesign
- Mobile-friendly collapsed filter-and-control area
- Flash panel and timeline-style feed presentation (flash panel later removed in Stage 7)
- Source status side panel
- Hot topic side panel

## Stage 5: DeepL Translation Provider

Status: completed

Delivered:

- `TRANSLATION_PROVIDER` config switch (`deepl` vs OpenAI-compatible)
- DeepL Free API integration (`https://api-free.deepl.com/v2/translate`), full title batch translated
- Budgeted per-run translation cap (`TRANSLATION_MAX_ITEMS_PER_RUN`) with cron-driven backfill
- DeepL quality verified on mixed English titles (incl. Chinese rendering)

Validation completed:

- Full 222-title batch translated in one run
- `translator.py` OpenAI-compatible path preserved as fallback

## Stage 6: Dark Premium UI + Font + Layout Refactor

Status: completed

Delivered:

- Dark theme: deep ink-blue background (`#181d26`), gold accents (`#c9a86a` / `#e0c28a`), radial gold glow
- Serif reading typography (Noto Serif SC) + Cormorant Garamond numerals, size/weight/leading tuned
- Emphasized titles, de-emphasized summaries; removed source meta line above titles
- Streamlit top chrome hidden; brand + gold clock hero bar pinned as a **fixed** top bar
- Filter/control panel pinned below the hero (fixed, scrollable inner area)
- Pinning fixed with headless-Chrome verification (Streamlit 1.61 expander is a `div[data-testid=stExpander]`, not `details`)
- Background lightened on request (`#0b0d11` → `#12161e` → `#181d26`)

Validation completed:

- Streamlit AppTest render pass
- Headless Chrome (playwright + system Chrome) checks of computed styles and post-scroll positions

## Stage 7: Product Cleanup And Commodity Sources

Status: completed

Delivered:

- Removed importance UI: score chips, importance sorting, priority accents, and the flash (重要快讯) panel
- Feed now always time-descending; `原文` link inlined at the end of the summary
- Added 8 commodity/news sources: OilPrice.com, Mining.com, The Western Producer, MarketWatch, FreightWaves, Seeking Alpha, Investing.com Commodities, CoinDesk (collectors 13 → 21)
- Browser User-Agent added to `parse_feed()` to pass bot-blocked feeds (e.g. Mining.com 403)
- Timezone fix: naive RSS timestamps treated as UTC (was interpreted as server-local PDT, causing +7h future times on Investing.com items); corrected stored rows
- Git repo published to github.com/dipui9707/global-market-news (main); `.env` backups and `.venv` ignored
- Deployment guide added (`DEPLOYMENT.md`), `.env.example` aligned to DeepL

Validation completed:

- All 21 sources render in the UI filter list; ingestion and translation verified per source
- Clone + fresh install + empty-DB init + render verified end-to-end

## Current Baseline

The repository currently represents:

- Python 3.12 runtime (Ubuntu 24.04, Los Angeles VPS)
- SQLite-backed MVP
- 21 live sources: macro/media, official agencies, AI industry, commodity futures, crypto
- Rule-based enrichment pipeline
- DeepL title translation (default), OpenAI-compatible fallback preserved
- Dark premium UI with fixed top bar (brand + gold clock + pinned filters), Noto Serif SC typography
- Pure time-descending feed without importance UI or flash panel
- cron-driven ingestion every 5 minutes
- `.env.example` and runtime assumptions aligned to `deepl`
- Incremental history browsing, duplicate-story collapsing, retention cap, WAL + busy timeout
- Optional websocket-backed MktNews live cache bridge
- systemd deployment (port 8501) with cron ingestion; deployment guide covers Docker / PaaS paths

## Next Suggested Work

- Improve cross-source event clustering
- Make source status reflect real collector success/failure
- Add event-centric and topic-centric research views
- Harden source adapters and feed quality (some sites 401/403 intermittently)
- Optional: nginx reverse proxy + auth for public exposure of port 8501
- Optional: logrotate for pipeline logs
