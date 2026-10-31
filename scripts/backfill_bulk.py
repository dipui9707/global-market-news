import sys, time, sqlite3
sys.path.insert(0, "/root/global-market-news/src")
from concurrent.futures import ThreadPoolExecutor
from news_mvp.config import get_settings
from news_mvp.db import connection_scope
from news_mvp.pipeline.translator import (
    HIDDEN_SOURCES, should_translate_text, translate_titles_batch,
    update_article_translations,
)

s = get_settings()
NSHARDS = 5
LIMIT = 20

def backfill_shard(shard: int) -> int:
    query = f"""
        SELECT id, title, language, title_zh FROM articles
        WHERE COALESCE(published_at, fetched_at) >= datetime('now', ?)
          AND source NOT IN ({", ".join("?" for _ in HIDDEN_SOURCES)})
          AND (rowid % ?) = ?
        ORDER BY importance_score DESC, COALESCE(published_at, fetched_at) DESC
    """
    params = [f"-{s.default_lookback_hours} hours", *HIDDEN_SOURCES, NSHARDS, shard]
    total = 0
    fail_streak = 0
    while True:
        with connection_scope(s) as connection:
            rows = connection.execute(query, params).fetchall()
            pending = []
            for r in rows:
                if should_translate_text(text=r["title"], language=r["language"], existing_translation=r["title_zh"]):
                    pending.append(r)
                    if len(pending) >= LIMIT:
                        break
            if not pending:
                return total
            results = translate_titles_batch([r["title"] for r in pending], s)
            done = 0
            for r, zh in zip(pending, results):
                if not zh:
                    continue
                for attempt in range(4):
                    try:
                        update_article_translations(connection, r["id"], title_zh=zh)
                        done += 1
                        break
                    except sqlite3.OperationalError:
                        if attempt == 3:
                            break
                        time.sleep(1.0 * (attempt + 1))
            total += done
            print(f"[shard{shard}] +{done} (累计{total})", flush=True)
            if done == 0:
                fail_streak += 1
                if fail_streak >= 3:
                    print(f"[shard{shard}] 连续3轮失败，退出（待cron续翻）", flush=True)
                    return total
                time.sleep(5)
            else:
                fail_streak = 0

if __name__ == "__main__":
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=NSHARDS) as ex:
        results = list(ex.map(backfill_shard, range(NSHARDS)))
    print(f"DONE: 共补翻 {sum(results)} 条, 耗时 {time.time()-t0:.1f}s")
