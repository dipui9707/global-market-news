from __future__ import annotations

import streamlit as st

from news_mvp.config import get_settings
from news_mvp.db import initialize_database
from news_mvp.dashboard.ui import render_dashboard


@st.cache_resource
def _initialize_app(settings_fingerprint: tuple[str, str]) -> None:
    settings = get_settings()
    initialize_database(settings)


def _inject_auto_reload(settings) -> None:
    """若 AUTO_UPDATE_ENABLED=true，页面定时自动重载（保留滚动位置）。"""
    if not settings.auto_update_enabled:
        return
    seconds = max(int(settings.auto_update_interval_seconds), 60)
    st.markdown(
        f"""
        <script>
        (function() {{
            var KEY = "gmn_scroll_top";
            var saved = sessionStorage.getItem(KEY);
            if (saved !== null) {{
                window.scrollTo(0, parseInt(saved, 10) || 0);
                sessionStorage.removeItem(KEY);
            }}
            setTimeout(function() {{
                sessionStorage.setItem(KEY, String(window.scrollY));
                location.reload();
            }}, {seconds * 1000});
        }})();
        </script>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    settings = get_settings()
    _initialize_app((settings.app_env, settings.database_url))
    st.set_page_config(
        page_title="Financial Intelligence Feedboard",
        page_icon=":newspaper:",
        layout="wide",
    )
    _inject_auto_reload(settings)
    render_dashboard(settings)


if __name__ == "__main__":
    main()
