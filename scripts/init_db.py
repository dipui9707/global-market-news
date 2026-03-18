from __future__ import annotations

from news_mvp.config import get_settings
from news_mvp.db import initialize_database


def main() -> None:
    settings = get_settings()
    initialize_database(settings)
    print(f"Database initialized at: {settings.database_path}")


if __name__ == "__main__":
    main()
