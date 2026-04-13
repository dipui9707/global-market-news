from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
import time

import streamlit as st

from news_mvp.config import Settings
from news_mvp.dashboard.components import (
    render_feed_item,
    render_flash_panel,
    render_header,
    render_mktnews_live_status,
    render_notes_panel,
    render_stat_panel,
    render_source_status_panel,
    render_topic_panel,
)
from news_mvp.dashboard.queries import (
    load_article_feed,
    load_dashboard_stats,
    load_filter_options,
    load_flash_items,
    load_mktnews_live_status,
    load_source_status,
    load_topic_pulse,
    SourceStatus,
)
from news_mvp.dashboard.styles import get_dashboard_css
from news_mvp.pipeline.orchestrator import list_collectors, run_pipeline
from news_mvp.pipeline.translator import backfill_recent_translations, translation_is_configured


AUTO_UPDATE_INTERVAL_OPTIONS = [60, 120, 300, 600, 900, 1800]
INITIAL_FEED_PAGE_SIZE = 100
FEED_PAGE_STEP = 100
BJ_TZ = timezone(timedelta(hours=8))


def _init_auto_update_state(settings: Settings) -> None:
    st.session_state.setdefault("auto_update_enabled", settings.auto_update_enabled)
    st.session_state.setdefault("auto_update_interval_seconds", settings.auto_update_interval_seconds)
    st.session_state.setdefault("auto_update_last_run_ts", time.time())
    st.session_state.setdefault("auto_update_status", "自动刷新已就绪")
    st.session_state.setdefault("auto_update_running", False)


@st.fragment(run_every=1)
def _auto_update_heartbeat(settings: Settings) -> None:
    enabled = bool(st.session_state.get("auto_update_enabled", False))
    interval_seconds = int(st.session_state.get("auto_update_interval_seconds", settings.auto_update_interval_seconds))
    last_run_ts = float(st.session_state.get("auto_update_last_run_ts", time.time()))
    now_ts = time.time()

    if not enabled:
        return
    if st.session_state.get("auto_update_running", False):
        return
    if now_ts - last_run_ts < interval_seconds:
        return

    st.session_state["auto_update_running"] = True
    st.session_state["auto_update_status"] = "自动刷新页面中…"
    try:
        st.session_state["auto_update_last_run_ts"] = time.time()
        st.session_state["auto_update_status"] = "自动刷新已完成"
    except Exception as exc:
        st.session_state["auto_update_last_run_ts"] = time.time()
        st.session_state["auto_update_status"] = f"自动刷新失败 · {exc}"
    finally:
        st.session_state["auto_update_running"] = False
    st.rerun()


def _format_auto_update_note() -> str:
    enabled = bool(st.session_state.get("auto_update_enabled", False))
    interval_seconds = int(st.session_state.get("auto_update_interval_seconds", 300))
    last_run_ts = st.session_state.get("auto_update_last_run_ts")
    status = st.session_state.get("auto_update_status", "自动刷新已就绪")
    if not enabled:
        return "自动刷新关闭"
    if last_run_ts:
        last_run = datetime.fromtimestamp(float(last_run_ts), UTC).astimezone(BJ_TZ).strftime("%H:%M:%S")
        return f"{status} · 每 {interval_seconds} 秒 · 上次 {last_run} 北京时间"
    return f"{status} · 每 {interval_seconds} 秒"


def _reset_feed_pagination(settings: Settings) -> None:
    st.session_state["feed_visible_count"] = max(settings.default_page_size, INITIAL_FEED_PAGE_SIZE)


def _sync_feed_pagination(
    settings: Settings,
    *,
    hours: int,
    region: str,
    topic: str,
    search: str,
    sort_by: str,
    selected_source: str,
) -> None:
    current_signature = (hours, region, topic, search.strip(), sort_by, selected_source)
    previous_signature = st.session_state.get("feed_filter_signature")
    if previous_signature != current_signature:
        st.session_state["feed_filter_signature"] = current_signature
        _reset_feed_pagination(settings)


def render_dashboard(settings: Settings) -> None:
    _init_auto_update_state(settings)
    _auto_update_heartbeat(settings)
    st.markdown(get_dashboard_css(), unsafe_allow_html=True)
    render_header()

    stats = load_dashboard_stats(settings)
    filter_options = load_filter_options(settings)
    collector_names = list_collectors()

    st.markdown(f"<div class='status-ribbon'>● {_format_auto_update_note()}</div>", unsafe_allow_html=True)

    with st.expander("筛选与控制", expanded=False):
        render_stat_panel("总条数", str(stats.article_count))

        st.markdown("<div class='inline-kicker'>资讯源</div>", unsafe_allow_html=True)
        source_options = ["全部"] + filter_options["source"]
        selected_source = st.radio(
            "资讯源",
            source_options,
            horizontal=True,
            label_visibility="collapsed",
            index=0,
        )

        hours = st.selectbox("时间窗口", [24, 72, 168, 720], index=1, format_func=lambda x: f"{x} 小时")
        region = st.selectbox("区域", ["全部"] + filter_options["region"], index=0)
        topic = st.selectbox("主题", ["全部"] + filter_options["topic"], index=0)
        search = st.text_input("搜索", placeholder="搜索标题、标签或事件…")
        sort_by = st.selectbox(
            "排序",
            ["time", "importance"],
            index=0,
            format_func=lambda x: "时间降序" if x == "time" else "重要性降序",
        )
        interval_seconds = st.selectbox(
            "刷新间隔",
            AUTO_UPDATE_INTERVAL_OPTIONS,
            index=(
                AUTO_UPDATE_INTERVAL_OPTIONS.index(st.session_state.get("auto_update_interval_seconds"))
                if st.session_state.get("auto_update_interval_seconds") in AUTO_UPDATE_INTERVAL_OPTIONS
                else AUTO_UPDATE_INTERVAL_OPTIONS.index(settings.auto_update_interval_seconds)
                if settings.auto_update_interval_seconds in AUTO_UPDATE_INTERVAL_OPTIONS
                else 2
            ),
            format_func=lambda value: f"{value} 秒",
        )
        if interval_seconds != st.session_state.get("auto_update_interval_seconds"):
            st.session_state["auto_update_interval_seconds"] = interval_seconds
            st.session_state["auto_update_last_run_ts"] = time.time()
            st.session_state["auto_update_status"] = f"自动刷新间隔已调整为 {interval_seconds} 秒"
            st.rerun()

        st.markdown("<div class='control-action-group'></div>", unsafe_allow_html=True)
        expander_action, expander_translate, expander_auto_toggle = st.columns([1, 1, 1], gap="medium")
        with expander_action:
            st.markdown("<div class='control-caption'>数据抓取</div>", unsafe_allow_html=True)
            if st.button("重新抓取", use_container_width=True, type="primary"):
                with st.spinner("Running collection and processing pipeline..."):
                    result = run_pipeline(settings)
                st.session_state["auto_update_last_run_ts"] = time.time()
                st.session_state["auto_update_status"] = (
                    f"手动更新完成 · collected {result.collected_count} · stored {result.stored_count}"
                )
                st.success(
                    f"Pipeline finished: collected {result.collected_count}, "
                    f"stored {result.stored_count}, duplicates {result.duplicate_count}."
                )
                st.rerun()
        with expander_translate:
            st.markdown("<div class='control-caption'>翻译操作</div>", unsafe_allow_html=True)
            translate_disabled = not translation_is_configured(settings)
            if st.button("补全翻译", use_container_width=True, disabled=translate_disabled, type="secondary"):
                with st.spinner("Translating high-priority items..."):
                    translated = backfill_recent_translations(
                        settings,
                        hours=hours,
                        limit=settings.translation_max_items_per_run,
                    )
                if translated > 0:
                    st.success(f"补全翻译完成：已更新 {translated} 条标题翻译。")
                else:
                    st.info("当前时间窗口内没有新的未翻译外文标题。")
                st.rerun()
        with expander_auto_toggle:
            st.markdown("<div class='control-caption'>自动刷新</div>", unsafe_allow_html=True)
            auto_enabled = st.toggle(
                "自动刷新",
                value=bool(st.session_state.get("auto_update_enabled", settings.auto_update_enabled)),
                help="打开后页面会按设定间隔自动刷新展示内容，抓取由服务器定时任务负责",
            )
            if auto_enabled != st.session_state.get("auto_update_enabled"):
                st.session_state["auto_update_enabled"] = auto_enabled
                st.session_state["auto_update_last_run_ts"] = time.time()
                st.session_state["auto_update_status"] = "自动刷新已开启" if auto_enabled else "自动刷新已关闭"
                st.rerun()

    hours = locals().get("hours", 72)
    region = locals().get("region", "全部")
    topic = locals().get("topic", "全部")
    search = locals().get("search", "")
    sort_by = locals().get("sort_by", "time")
    selected_source = locals().get("selected_source", "全部")

    _sync_feed_pagination(
        settings,
        hours=hours,
        region=region,
        topic=topic,
        search=search,
        sort_by=sort_by,
        selected_source=selected_source,
    )
    visible_count = min(
        int(st.session_state.get("feed_visible_count", max(settings.default_page_size, INITIAL_FEED_PAGE_SIZE))),
        settings.article_retention_count,
    )

    flash_items = load_flash_items(settings, hours=hours, limit=5)
    source_status_rows = load_source_status(settings, hours=hours)
    source_status_map = {row.source: row for row in source_status_rows}
    source_status = []
    display_sources = filter_options["source"] or collector_names
    for source_name in display_sources:
        row = source_status_map.get(source_name)
        if row is None:
            source_status.append(SourceStatus(source=source_name, article_count=0, latest_published_at=None, status="idle"))
        else:
            source_status.append(row)
    mktnews_live_status = load_mktnews_live_status(settings)
    topic_pulse = load_topic_pulse(settings, hours=hours, limit=8)
    articles = load_article_feed(
        settings,
        hours=hours,
        topic=None if topic == "全部" else topic,
        region=None if region == "全部" else region,
        source=None if selected_source == "全部" else selected_source,
        search=search or None,
        sort_by=sort_by,
        limit=visible_count,
    )

    main_col, side_col = st.columns([4.8, 1.45], gap="large")

    with main_col:
        render_flash_panel(flash_items)
        for article in articles:
            render_feed_item(article)
        if articles:
            st.caption(f"当前已显示 {len(articles)} 条，最多可逐步查看至 {settings.article_retention_count} 条保留内容。")
            if len(articles) >= visible_count and visible_count < settings.article_retention_count:
                if st.button("加载更多", key="load_more_articles", use_container_width=True):
                    st.session_state["feed_visible_count"] = min(
                        visible_count + FEED_PAGE_STEP,
                        settings.article_retention_count,
                    )
                    st.rerun()
        if not articles:
            st.info("当前筛选条件下暂无结果，请调整来源、主题、区域或时间窗口。")

    with side_col:
        render_mktnews_live_status(mktnews_live_status)
        render_source_status_panel(source_status)
        render_topic_panel(topic_pulse)
        render_notes_panel()
