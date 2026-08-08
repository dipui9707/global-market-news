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
    """若 AUTO_UPDATE_ENABLED=true，页面每 N 秒自动重载拉取最新数据。

    用一个 1px 同源 iframe（st.iframe，允许 JS + 同源访问）承载定时器，
    到点后刷新顶层页面。若自动刷新被禁用则不注入。
    """
    if not settings.auto_update_enabled:
        return
    seconds = max(int(settings.auto_update_interval_seconds), 60)
    # st.html 的 unsafe_allow_javascript 允许 script 执行；到点整页刷新拉取最新数据
    st.html(
        f"""<script>
        window.__gmn_autorefresh_ms = {seconds * 1000};
        setTimeout(function() {{
            window.location.reload();
        }}, {seconds * 1000});
        </script>""",
        unsafe_allow_javascript=True,
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
