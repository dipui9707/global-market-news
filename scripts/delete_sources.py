"""删除指定信息源的数据库数据（articles 及其关联表）"""
import sys

sys.path.insert(0, "/root/global-market-news/src")

import sqlite3

from news_mvp.config import get_settings

SOURCES = ("CNBC", "FreightWaves", "The Western Producer")


def main() -> None:
    settings = get_settings()
    conn = sqlite3.connect(settings.database_path)
    placeholders = ", ".join("?" for _ in SOURCES)

    before = conn.execute(
        f"SELECT source, COUNT(*) FROM articles WHERE source IN ({placeholders}) GROUP BY source",
        SOURCES,
    ).fetchall()
    print("删除前:", before)

    conn.execute(
        f"DELETE FROM article_tags WHERE article_id IN (SELECT id FROM articles WHERE source IN ({placeholders}))",
        SOURCES,
    )
    conn.execute(
        f"DELETE FROM article_event_map WHERE article_id IN (SELECT id FROM articles WHERE source IN ({placeholders}))",
        SOURCES,
    )
    cur = conn.execute(
        f"DELETE FROM articles WHERE source IN ({placeholders})", SOURCES
    )
    deleted_articles = cur.rowcount
    conn.commit()

    after = conn.execute(
        f"SELECT COUNT(*) FROM articles WHERE source IN ({placeholders})", SOURCES
    ).fetchone()[0]
    print(f"已删除文章: {deleted_articles} 条；剩余: {after} 条")

    # 校验
    for t in ("articles", "article_tags", "article_event_map"):
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {n} 行")
    conn.close()


if __name__ == "__main__":
    main()
