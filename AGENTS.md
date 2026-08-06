# AGENTS

This repository is developed as a staged MVP for a financial intelligence aggregation dashboard,
currently running as a Streamlit app on a Los Angeles VPS (Ubuntu 24.04, Python 3.12, systemd, port 8501).

## Project Principles

- Keep the scope tightly focused on the MVP pipeline.
- Prefer stable public feeds and official pages over brittle browser automation.
- Keep the project runnable after every stage.
- Do not introduce heavy infrastructure before the pipeline is proven.
- Avoid storing or displaying copyrighted full-text content when title, link, metadata, and derived analysis are sufficient.
- Prefer practical progress on the research workflow over feature breadth.
- Commodity futures (energy, metals, agriculture, shipping) are a first-class focus alongside macro media.

## Architecture Rules

- Use Python and Streamlit for the initial MVP.
- Use SQLite first, but isolate DB configuration and access so PostgreSQL can be introduced later.
- Keep scoring logic in a dedicated module even if the UI does not surface scores.
- Keep collectors source-specific and normalize them into a shared article payload structure.
- Keep pipeline steps separate: cleaning, deduplication, tagging, summarization, clustering, scoring.
- Keep dashboard data access in `dashboard/queries.py` and presentation logic in `dashboard/components.py` and `dashboard/ui.py`.
- Adding a new RSS source touches three places: the collector class, `collectors/__init__.py` registration, and `orchestrator.py` `get_collectors()`.

## Product Rules

- This product is a financial intelligence feedboard, not a generic news homepage.
- Optimize for scan speed, research usefulness, and advisory workflow support.
- The UI is a **dark premium theme**: deep ink-blue background (`#181d26`), gold accents (`#c9a86a`), Noto Serif SC serif body, Cormorant Garamond numerals. Keep it visually coherent with this direction.
- The top bar (brand + clock + filters) is **fixed**; preserve the fixed top-bar and pinned filter layout.
- Emphasize titles, de-emphasize summaries. Do not reintroduce importance badges, importance sorting, or the flash (重要快讯) panel unless explicitly requested.
- Default feed behavior prioritizes latest information (time descending).
- Interface copy is Chinese; keep it consistent.

## Source Rules

- Prefer official feeds and stable public endpoints.
- Avoid brittle browser automation as a first option.
- If a source is only reachable through an intermediary feed, document that tradeoff clearly.
- Source health shown in the UI should reflect actual collector behavior where possible, not fabricated success.
- When adding a source, verify RSS reachability from the server before integrating (403/404/SPA-only feeds are common).

## Data Rules

- Titles, links, summaries, derived tags, scores, and event grouping are the primary user-facing artifacts.
- Do not optimize for storing or presenting large copyrighted article bodies.
- Rule-based implementations are acceptable in MVP as long as they are explicit and replaceable.
- Duplicate-story collapsing in the main feed is acceptable as long as raw source rows are still retained in SQLite.
- Translation is title-only; keep summaries in the source language.
- The data layer may keep fields the UI no longer shows (e.g. `importance_score`) to avoid breaking the pipeline.

## Environment Rules

- The production runtime is Python 3.12 on Ubuntu 24.04; the code requires Python >= 3.11 (`datetime.UTC`).
- Do not reintroduce temporary Python side environments or translation stacks unless explicitly requested.
- Translation defaults to DeepL (`TRANSLATION_PROVIDER=deepl`); the OpenAI-compatible path (Qwen/DashScope) remains as an optional fallback.
- Keep `.env.example` aligned with the actual supported runtime options. Secrets (`.env`, `.env.bak-*`) must never be committed.

## Delivery Rules

- Update `PLANS.md` as stages progress.
- Update `README.md` and `AGENTS.md` when product scope, runtime assumptions, or dashboard interaction patterns change.
- Prefer small, focused diffs over broad refactors.
- If a real integration is not yet ready, implement an explicit placeholder rather than pretending it works.
- Verify UI changes with the Streamlit AppTest render pass, and verify visual/positioning changes with headless browser checks when needed.
- Before pushing, ensure sensitive files (`.env`, backups, `data/`, `.venv/`) are ignored and not staged.
