from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo

import streamlit as st

from news_mvp.collectors.base import sanitize_text
from news_mvp.dashboard.queries import ArticleCard, SourceStatus, TopicPulse

BJ_TZ = timezone(timedelta(hours=8))
NY_TZ = ZoneInfo("America/New_York")
LON_TZ = ZoneInfo("Europe/London")


def render_header() -> None:
    now = datetime.now(UTC)
    bj = now.astimezone(BJ_TZ).strftime("%H:%M")
    ny = now.astimezone(NY_TZ).strftime("%H:%M")
    lon = now.astimezone(LON_TZ).strftime("%H:%M")
    html = f"""
    <div class="hero-bar">
        <div class="hero-left">
            <div class="brand-title">环球财经</div>
            <div class="brand-sub">Global Market News</div>
        </div>
        <div class="market-clock">北京 {bj} &nbsp;&nbsp;•&nbsp;&nbsp; NY {ny} &nbsp;&nbsp;•&nbsp;&nbsp; LON {lon}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_feed_item(article: ArticleCard) -> None:
    published = article.published_at or article.fetched_at
    dt = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else None
    bj_dt = dt.astimezone(BJ_TZ) if dt else None
    main_time = bj_dt.strftime("%H:%M") if bj_dt else "--:--"
    ago = _relative_time(dt) if dt else "未知"
    clean_title = sanitize_text(article.title)
    clean_title_zh = sanitize_text(article.title_zh)
    clean_summary = sanitize_text(article.summary)
    display_summary = clean_summary or "No summary available."
    display_title = clean_title_zh if clean_title_zh and clean_title_zh != clean_title else clean_title
    badges = [f"<span class='badge source'>{escape(article.source)}</span>"]
    for tag in article.topic_tags[:3]:
        badges.append(f"<span class='badge'>{escape(tag)}</span>")
    for tag in article.asset_tags[:2]:
        badges.append(f"<span class='badge'>{escape(tag)}</span>")
    if article.event_type:
        badges.append(f"<span class='badge'>{escape(article.event_type)}</span>")
    if article.is_duplicate:
        duplicate_label = "重复链接" if article.dedup_reason == "same_url" else "重复报道"
        badges.append(f"<span class='badge duplicate'>{duplicate_label}</span>")
    html = (
        f"<div class=\"feed-card\">"
        "<div class=\"feed-layout\">"
        "<div class=\"time-col\">"
        f"<div class=\"time-main\">{main_time}</div>"
        f"<div>{ago}</div>"
        "</div>"
        "<div>"
        f"<div class=\"feed-title\">{escape(display_title)}</div>"
        f"<div class=\"badge-row\">{''.join(badges)}</div>"
        f"<div class=\"summary-text\">{escape(display_summary)} <a href=\"{escape(article.url)}\" target=\"_blank\" class=\"feed-link\">原文</a></div>"
        "</div>"
        "</div>"
        "</div>"
    )
    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_source_status_panel(items: list[SourceStatus]) -> None:
    rows = "".join(
        f"""
        <div class="side-row">
            <div>
                <span class="side-dot {escape(item.status)}"></span>{escape(item.source)}
                <div class="side-sub">{escape(_format_source_time(item.latest_published_at))}</div>
            </div>
            <div class="side-count">{item.article_count} 条</div>
        </div>
        """
        for item in items
    ) or "<div class='mono-note'>暂无来源状态</div>"
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">来源状态</div>
            <div class="side-list">{rows}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topic_panel(items: list[TopicPulse]) -> None:
    rows = "".join(
        f"<span class='topic-chip'>{escape(item.topic_name)} <strong>{item.article_count}</strong></span>"
        for item in items
    ) or "<div class='mono-note'>暂无热门主题</div>"
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">热门话题</div>
            <div class="topic-wrap">{rows}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_notes_panel() -> None:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">说明</div>
            <div class="mono-note">
                • 当前以稳定公开 feed 为优先抓取方式。<br/>
                • 看板为研究导向信息流，不展示大段原文全文。<br/>
                • 主 feed 默认折叠重复报道，仅展示每组代表新闻。<br/>
                • 评分、标签、事件归类仍为规则版 MVP。<br/>
                • 数据更新需手动点击「重新抓取」按钮，或由服务器定时任务触发。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_panel(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="stat-panel control-box">
            <div class="stat-label">{escape(label)}</div>
            <div class="stat-value">{escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _relative_time(dt: datetime) -> str:
    delta_minutes = int((datetime.now(UTC) - dt.astimezone(UTC)).total_seconds() // 60)
    if delta_minutes < 60:
        return f"{max(delta_minutes, 1)} 分前"
    hours = delta_minutes // 60
    if hours < 24:
        return f"{hours} 小时前"
    return f"{hours // 24} 天前"


def _format_source_time(value: str | None) -> str:
    if not value:
        return "无更新"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(BJ_TZ)
    except ValueError:
        return "无更新"
    return dt.strftime("%H:%M")



