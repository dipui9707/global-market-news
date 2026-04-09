# AGENTS

This repository is developed as a staged MVP for a financial intelligence aggregation dashboard.

## Project Principles

- Keep the scope tightly focused on the MVP pipeline.
- Prefer stable public feeds and official pages over brittle browser automation.
- Keep the project runnable after every stage.
- Do not introduce heavy infrastructure before the pipeline is proven.
- Avoid storing or displaying copyrighted full-text content when title, link, metadata, and derived analysis are sufficient.
- Prefer practical progress on the research workflow over feature breadth.

## Architecture Rules

- Use Python and Streamlit for the initial MVP.
- Use SQLite first, but isolate DB configuration and access so PostgreSQL can be introduced later.
- Keep scoring logic in a dedicated module.
- Keep collectors source-specific and normalize them into a shared article payload structure.
- Keep pipeline steps separate: cleaning, deduplication, tagging, summarization, clustering, scoring.
- Keep dashboard data access in `dashboard/queries.py` and presentation logic in `dashboard/components.py` and `dashboard/ui.py`.

## Product Rules

- This product is a financial intelligence feedboard, not a generic news homepage.
- Optimize for scan speed, research usefulness, and advisory workflow support.
- High-density layouts are acceptable when they improve information throughput.
- Keep the dashboard visually coherent with the current light paper-toned research-board design unless the product direction changes.
- Default feed behavior should prioritize latest information unless the user explicitly changes sorting.

## Source Rules

- Prefer official feeds and stable public endpoints.
- Avoid brittle browser automation as a first option.
- If a source is only reachable through an intermediary feed, document that tradeoff clearly.
- Source health shown in the UI should reflect actual collector behavior where possible, not fabricated success.

## Data Rules

- Titles, links, summaries, derived tags, scores, and event grouping are the primary user-facing artifacts.
- Do not optimize for storing or presenting large copyrighted article bodies.
- Rule-based implementations are acceptable in MVP as long as they are explicit and replaceable.
- Duplicate-story collapsing in the main feed is acceptable as long as raw source rows are still retained in SQLite.
- If translation is enabled, default to title-only translation unless the product direction explicitly broadens that scope.

## Environment Rules

- The default local runtime is Python 3.14.
- Do not reintroduce temporary Python side environments or translation stacks unless explicitly requested.
- Optional title-only translation support through configurable external model APIs is acceptable when explicitly requested and must remain configurable rather than mandatory.
- Keep `.env.example` aligned with the actual supported runtime options.

## Delivery Rules

- Update `PLANS.md` as stages progress.
- Update `README.md` and `AGENTS.md` when product scope, runtime assumptions, or dashboard interaction patterns change.
- Prefer small, focused diffs over broad refactors.
- If a real integration is not yet ready, implement an explicit placeholder rather than pretending it works.
- Dashboard interaction changes should preserve both manual refresh and any existing auto-update workflow unless a product change explicitly removes one.
- Mobile interaction changes should preserve a collapsed control area pattern and keep first-screen content focused on the feed.
