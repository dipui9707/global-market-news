from __future__ import annotations

import streamlit as st

from news_mvp.config import Settings
from news_mvp.dashboard.components import (
    render_feed_item,
    render_header,
    render_notes_panel,
    render_stat_panel,
    render_source_status_panel,
    render_topic_panel,
    render_translation_activity,
)
from news_mvp.dashboard.queries import (
    load_article_feed,
    load_dashboard_stats,
    load_filter_options,
    load_source_status,
    load_topic_pulse,
    SourceStatus,
)
from news_mvp.dashboard.styles import get_dashboard_css
from news_mvp.pipeline.orchestrator import list_collectors, run_pipeline
from news_mvp.pipeline.translator import backfill_recent_translations, translation_is_configured


INITIAL_FEED_PAGE_SIZE = 100
FEED_PAGE_STEP = 100


def _render_feed_section(
    settings: Settings,
    *,
    hours: int,
    region: str,
    topic: str,
    search: str,
    sort_by: str,
    selected_source: str,
) -> None:
    """渲染主 feed 区块。

    注意：必须定义为模块级函数，所有依赖通过显式参数传入。
    Streamlit 的 fragment rerun 会用捕获的参数重放本函数；若依赖外层
    闭包变量（嵌套函数场景），重放时变量不存在会静默渲染失败，页面
    停留在初始渲染的旧数据（历史 bug）。
    """
    visible_count = min(
        int(st.session_state.get("feed_visible_count", max(settings.default_page_size, INITIAL_FEED_PAGE_SIZE))),
        settings.article_retention_count,
    )
    render_translation_activity(settings)
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


def _render_feed_section_with_auto_refresh(
    settings: Settings,
    *,
    hours: int,
    region: str,
    topic: str,
    search: str,
    sort_by: str,
    selected_source: str,
) -> None:
    """以 st.fragment(run_every=...) 包装主 feed，实现定时局部刷新。

    用运行时调用式包装（而非装饰器），使 run_every 能根据配置动态决定。
    fragment 重放时以捕获的参数调用模块级 _render_feed_section，
    不再依赖外层闭包。
    """
    run_every = (
        max(int(settings.auto_update_interval_seconds), 60)
        if settings.auto_update_enabled
        else None
    )
    fragment_fn = st.fragment(run_every=run_every)(_render_feed_section)
    fragment_fn(
        settings,
        hours=hours,
        region=region,
        topic=topic,
        search=search,
        sort_by=sort_by,
        selected_source=selected_source,
    )


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
    st.markdown(get_dashboard_css(), unsafe_allow_html=True)
    render_header(settings)

    stats = load_dashboard_stats(settings)
    filter_options = load_filter_options(settings)
    collector_names = list_collectors()

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


        st.markdown("<div class='control-action-group'></div>", unsafe_allow_html=True)
        action_col, translate_col = st.columns([1, 1], gap="medium")
        with action_col:
            st.markdown("<div class='control-caption'>数据抓取</div>", unsafe_allow_html=True)
            if st.button("重新抓取", use_container_width=True, type="primary"):
                with st.spinner("Running collection and processing pipeline..."):
                    result = run_pipeline(settings)
                st.success(
                    f"Pipeline finished: collected {result.collected_count}, "
                    f"stored {result.stored_count}, duplicates {result.duplicate_count}."
                )
                st.rerun()
        with translate_col:
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

    hours = locals().get("hours", 72)
    region = locals().get("region", "全部")
    topic = locals().get("topic", "全部")
    search = locals().get("search", "")
    sort_by = "time"
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
    topic_pulse = load_topic_pulse(settings, hours=hours, limit=8)

    # 主 feed 区块：定时局部自动刷新（类似金十的增量更新，不整页刷新）
    main_col, side_col = st.columns([4.8, 1.45], gap="large")

    with main_col:
        _render_feed_section_with_auto_refresh(
            settings,
            hours=hours,
            region=region,
            topic=topic,
            search=search,
            sort_by=sort_by,
            selected_source=selected_source,
        )

    with side_col:
        render_source_status_panel(source_status)
        render_topic_panel(topic_pulse)
        render_notes_panel()
