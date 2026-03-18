from __future__ import annotations

import streamlit as st

from news_mvp.config import get_settings
from news_mvp.db import initialize_database
from news_mvp.dashboard.ui import render_dashboard


def main() -> None:
    settings = get_settings()
    initialize_database(settings)
    st.set_page_config(
        page_title="Financial Intelligence Feedboard",
        page_icon=":newspaper:",
        layout="wide",
    )
    render_dashboard(settings)


if __name__ == "__main__":
    main()
