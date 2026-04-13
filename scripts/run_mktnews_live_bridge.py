from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

import websockets

from news_mvp.collectors.mktnews import fetch_mktnews_flash, parse_mktnews_timestamp
from news_mvp.config import ROOT_DIR, get_settings


WS_URL_TEMPLATE = "wss://api.mktnews.net?lang={lang}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Keep a local live cache of MktNews flash items via the public websocket feed."
    )
    parser.add_argument("--lang", default="en", help="MktNews websocket language, defaults to en.")
    parser.add_argument(
        "--bootstrap-limit",
        type=int,
        default=100,
        help="How many items to fetch from the REST bootstrap endpoint before listening to the websocket.",
    )
    parser.add_argument(
        "--heartbeat-timeout",
        type=int,
        default=90,
        help="Seconds to wait for a websocket message before reconnecting.",
    )
    parser.add_argument(
        "--runtime-seconds",
        type=int,
        default=0,
        help="Optional max runtime for testing. Zero means run forever.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Bootstrap from REST and write the cache once without opening the websocket.",
    )
    return parser


def load_existing_cache(cache_path: Path) -> list[dict[str, Any]]:
    if not cache_path.exists():
        return []
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    items = payload.get("items")
    if not isinstance(items, list):
        return []
    return [entry for entry in items if isinstance(entry, dict)]


def upsert_item(entries: dict[str, dict[str, Any]], item: dict[str, Any]) -> None:
    item_id = item.get("id")
    if not item_id:
        return
    current = entries.get(item_id)
    if current is None:
        entries[item_id] = item
        return
    current_time = parse_mktnews_timestamp(current.get("time"))
    next_time = parse_mktnews_timestamp(item.get("time"))
    if next_time and (current_time is None or next_time >= current_time):
        entries[item_id] = item


def remove_item(entries: dict[str, dict[str, Any]], item: dict[str, Any]) -> None:
    item_id = item.get("id")
    if item_id:
        entries.pop(item_id, None)


def trim_entries(entries: dict[str, dict[str, Any]], max_items: int) -> dict[str, dict[str, Any]]:
    sorted_items = sorted(
        entries.values(),
        key=lambda entry: parse_mktnews_timestamp(entry.get("time")) or "",
        reverse=True,
    )[:max_items]
    return {entry["id"]: entry for entry in sorted_items if entry.get("id")}


def write_cache(cache_path: Path, lang: str, entries: dict[str, dict[str, Any]]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    ordered_items = sorted(
        entries.values(),
        key=lambda entry: parse_mktnews_timestamp(entry.get("time")) or "",
        reverse=True,
    )
    payload = {
        "lang": lang,
        "updated_at": datetime.now(UTC).isoformat(),
        "items": ordered_items,
    }
    temp_path = cache_path.with_suffix(f"{cache_path.suffix}.tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    temp_path.replace(cache_path)


def bootstrap_entries(cache_path: Path, lang: str, bootstrap_limit: int, max_items: int) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for item in load_existing_cache(cache_path):
        upsert_item(entries, item)

    try:
        for item in fetch_mktnews_flash(limit=bootstrap_limit):
            upsert_item(entries, item)
    except Exception:
        pass

    entries = trim_entries(entries, max_items=max_items)
    write_cache(cache_path, lang=lang, entries=entries)
    return entries


async def stream_live_updates(
    cache_path: Path,
    lang: str,
    bootstrap_limit: int,
    heartbeat_timeout: int,
    max_items: int,
    runtime_seconds: int,
) -> None:
    entries = bootstrap_entries(cache_path, lang=lang, bootstrap_limit=bootstrap_limit, max_items=max_items)
    stop_at = asyncio.get_running_loop().time() + runtime_seconds if runtime_seconds > 0 else None

    while True:
        if stop_at is not None and asyncio.get_running_loop().time() >= stop_at:
            return
        try:
            async with websockets.connect(WS_URL_TEMPLATE.format(lang=lang), ping_interval=20, ping_timeout=20) as ws:
                while True:
                    if stop_at is not None and asyncio.get_running_loop().time() >= stop_at:
                        return
                    message = await asyncio.wait_for(ws.recv(), timeout=heartbeat_timeout)
                    payload = json.loads(message)
                    message_type = payload.get("type")
                    if message_type == "time":
                        await ws.send("")
                        continue
                    if message_type != "flash":
                        continue

                    action = payload.get("action")
                    item = payload.get("data") or {}
                    if not isinstance(item, dict):
                        continue

                    if action == 1 or action == 2:
                        upsert_item(entries, item)
                    elif action == 3:
                        remove_item(entries, item)
                    elif action == 6:
                        entries = bootstrap_entries(
                            cache_path=cache_path,
                            lang=lang,
                            bootstrap_limit=bootstrap_limit,
                            max_items=max_items,
                        )
                        continue

                    entries = trim_entries(entries, max_items=max_items)
                    write_cache(cache_path, lang=lang, entries=entries)
        except asyncio.TimeoutError:
            continue
        except websockets.WebSocketException:
            await asyncio.sleep(2)
        except OSError:
            await asyncio.sleep(2)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = get_settings()
    cache_path = ROOT_DIR / settings.mktnews_live_cache_path
    max_items = settings.mktnews_live_cache_max_items

    if args.once:
        bootstrap_entries(
            cache_path=cache_path,
            lang=args.lang,
            bootstrap_limit=args.bootstrap_limit,
            max_items=max_items,
        )
        print(f"Wrote MktNews cache to {cache_path}")
        return

    asyncio.run(
        stream_live_updates(
            cache_path=cache_path,
            lang=args.lang,
            bootstrap_limit=args.bootstrap_limit,
            heartbeat_timeout=args.heartbeat_timeout,
            max_items=max_items,
            runtime_seconds=args.runtime_seconds,
        )
    )


if __name__ == "__main__":
    main()
