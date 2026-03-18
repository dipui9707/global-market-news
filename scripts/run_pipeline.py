from __future__ import annotations

from news_mvp.config import get_settings
from news_mvp.pipeline.orchestrator import run_pipeline


def main() -> None:
    settings = get_settings()
    result = run_pipeline(settings)
    print("Pipeline status:", result.status)
    print("Message:", result.message)
    print("Collected:", result.collected_count)
    print("Stored:", result.stored_count)
    print("Duplicates:", result.duplicate_count)


if __name__ == "__main__":
    main()
