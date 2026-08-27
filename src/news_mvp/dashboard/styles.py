from __future__ import annotations


def get_dashboard_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@400;500;600;700;900&display=swap');

    :root {
        --bg: #181d26;
        --panel: rgba(22, 27, 35, 0.72);
        --panel-solid: #202734;
        --panel-2: rgba(26, 31, 40, 0.55);
        --line: rgba(255, 255, 255, 0.075);
        --line-strong: rgba(201, 168, 106, 0.28);
        --text: #ece6d6;
        --muted: #8f939c;
        --faint: #6b707a;
        --gold: #c9a86a;
        --gold-bright: #e0c28a;
        --gold-soft: rgba(201, 168, 106, 0.12);
        --green: #4cbfa0;
        --red: #d97a86;
    }

    .stApp {
        background:
            radial-gradient(ellipse 1100px 520px at 12% -8%, rgba(201, 168, 106, 0.07), transparent 62%),
            radial-gradient(ellipse 900px 460px at 96% 0%, rgba(96, 120, 180, 0.05), transparent 58%),
            linear-gradient(180deg, #181d26 0%, #161b23 46%, #141922 100%);
        color: var(--text);
        font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
    }

    /* 隐藏 Streamlit 顶部框架（菜单/Deploy/状态栏） */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    .block-container {
        padding-top: 0.9rem;
        padding-bottom: 1.2rem;
        max-width: 1400px;
    }

    /* ── Hero 顶栏粘性定位：让中间层 display:contents，
         使 sticky 包含块提升到 block-container，宽度与内容一致 ── */
    [data-testid="stMarkdownContainer"]:has(.hero-bar),
    [data-testid="stMarkdownContainer"]:has(.hero-bar) > div,
    [data-testid="stMarkdownContainer"]:has(.hero-bar) > div > div,
    [data-testid="stMarkdownContainer"]:has(.hero-bar) > div > div > div,
    [data-testid="stMarkdownContainer"]:has(.hero-bar) > div > div > div > div {
        display: contents;
    }

    /* ── Hero 固定顶栏（fixed，不随滚动） ──────── */
    .hero-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        background:
            linear-gradient(135deg, rgba(201, 168, 106, 0.09), transparent 46%),
            linear-gradient(180deg, rgba(20, 25, 33, 0.97), rgba(15, 19, 26, 0.94));
        border: 1px solid var(--line);
        border-top: 1px solid rgba(201, 168, 106, 0.35);
        border-radius: 18px 18px 0 0;
        padding: 1.15rem 1.25rem;
        margin-bottom: 0;
        min-height: 108px;
        margin-top: 0;
        box-shadow:
            0 24px 48px rgba(0, 0, 0, 0.42),
            inset 0 1px 0 rgba(255, 255, 255, 0.045);
        position: sticky;
        top: 0;
        z-index: 999;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        overflow: hidden;
    }

    .hero-bar::before {
        content: "";
        position: absolute;
        left: 1.25rem;
        right: 1.25rem;
        bottom: 0;
        height: 1px;
        background: linear-gradient(90deg, rgba(201, 168, 106, 0.55), transparent 72%);
        opacity: 0.8;
    }

    .hero-left {
        min-width: 220px;
    }

    .brand-title {
        color: var(--gold-bright);
        font-family: "Noto Serif SC", "Songti SC", serif;
        font-size: 1.8rem;
        line-height: 1.5;
        font-weight: 500;
        letter-spacing: 0.04em;
        padding-top: 0.2rem;
        padding-bottom: 0.14rem;
        margin: 0;
        white-space: nowrap;
        display: block;
        min-height: 2em;
        text-shadow: 0 0 24px rgba(201, 168, 106, 0.18);
    }

    .brand-sub {
        color: var(--muted);
        font-family: "Cormorant Garamond", Georgia, serif;
        font-size: 0.84rem;
        letter-spacing: 0.34em;
        text-transform: uppercase;
        font-weight: 500;
    }

    .market-clock {
        color: var(--gold-bright);
        font-family: "Cormorant Garamond", Georgia, serif;
        font-size: 0.94rem;
        letter-spacing: 0.1em;
        font-weight: 500;
    }

    /* ── 翻译活动条（feed 顶部，fragment 自动刷新） ── */
    .translation-activity {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.35rem 0.6rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 0.5rem;
        padding: 0.45rem 0.7rem;
        margin-bottom: 0.7rem;
        font-size: 0.72rem;
        color: var(--muted);
    }
    .ta-title {
        color: var(--gold-bright);
        letter-spacing: 0.12em;
        font-weight: 600;
        margin-right: 0.2rem;
    }
    .ta-item {
        font-family: ui-monospace, "SF Mono", Menlo, monospace;
        font-size: 0.68rem;
        color: var(--text);
        white-space: nowrap;
    }
    .ta-role-primary {
        color: #4cc9f0;
    }
    .ta-role-fallback {
        color: #f8961e;
    }
    .ta-ok {
        color: #74c69d;
    }
    .ta-fail {
        color: #e56b6f;
    }
    .ta-summary {
        color: var(--faint);
        margin-left: auto;
        font-size: 0.68rem;
    }

    /* ── 筛选与控制 ────────────────────────────── */
    .inline-kicker {
        color: var(--faint);
        font-size: 0.7rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
        font-weight: 500;
    }

    .control-caption {
        color: var(--muted);
        font-size: 0.72rem;
        min-height: 1.15rem;
        margin-bottom: 0.32rem;
        display: flex;
        align-items: center;
        font-weight: 500;
        letter-spacing: 0.04em;
    }

    .control-action-group {
        height: 0.35rem;
    }

    /* ── 面板卡片 ──────────────────────────────── */
    .section-card {
        background: linear-gradient(180deg, rgba(22, 27, 35, 0.82), rgba(16, 20, 27, 0.62));
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1rem 1.05rem;
        margin-bottom: 0.9rem;
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.035),
            0 16px 36px rgba(0, 0, 0, 0.3);
    }

    .section-title {
        color: var(--gold-bright);
        font-family: "Noto Serif SC", "Songti SC", serif;
        font-size: 0.92rem;
        margin-bottom: 0.6rem;
        letter-spacing: 0.1em;
        font-weight: 500;
    }

    /* ── Feed 卡片 ─────────────────────────────── */
    .feed-card {
        position: relative;
        border-top: 1px solid rgba(255, 255, 255, 0.055);
        border-radius: 14px;
        padding: 0.95rem 0.12rem 1rem 0.32rem;
        margin-top: 0.02rem;
        background: rgba(255, 255, 255, 0.012);
        transition: background 140ms ease, transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
    }

    .feed-card:hover {
        background:
            linear-gradient(180deg, rgba(201, 168, 106, 0.07), rgba(255, 255, 255, 0.015) 70%);
        transform: translateY(-1px);
        border-color: rgba(201, 168, 106, 0.3);
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
    }

    .feed-card::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0.78rem;
        bottom: 0.78rem;
        width: 2px;
        border-radius: 999px;
        background: transparent;
        transition: background 140ms ease, opacity 140ms ease;
        opacity: 0;
    }

    .feed-layout {
        display: grid;
        grid-template-columns: 60px 1fr;
        gap: 1.2rem;
        align-items: start;
    }

    .time-col {
        color: var(--faint);
        font-size: 0.66rem;
        text-align: right;
        padding-top: 0.12rem;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        padding-right: 0.78rem;
    }

    .time-main {
        color: var(--gold);
        font-family: "Cormorant Garamond", Georgia, serif;
        font-size: 1.06rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }

    .feed-title {
        color: #f2ecdd;
        font-family: "Noto Serif SC", "Songti SC", serif;
        font-size: 1.16rem;
        line-height: 1.62;
        font-weight: 400;
        margin: 0.08rem 0 0.4rem;
        letter-spacing: 0.01em;
    }

    .feed-title-zh {
        color: var(--gold-bright);
        font-family: "Noto Serif SC", "Songti SC", serif;
        font-size: 0.92rem;
        line-height: 1.62;
        margin: 0.1rem 0 0.4rem;
        font-weight: 400;
        letter-spacing: 0.015em;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.38rem;
        margin-bottom: 0.64rem;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        border: 1px solid rgba(201, 168, 106, 0.3);
        background: rgba(201, 168, 106, 0.08);
        color: var(--gold-bright);
        border-radius: 999px;
        font-size: 0.62rem;
        font-weight: 500;
        padding: 0.1rem 0.42rem;
        letter-spacing: 0.03em;
    }

    .badge.source {
        background: rgba(96, 130, 200, 0.12);
        border-color: rgba(96, 130, 200, 0.32);
        color: #a8bde0;
    }

    .badge.duplicate {
        background: rgba(217, 122, 134, 0.1);
        border-color: rgba(217, 122, 134, 0.3);
        color: #d99aa2;
    }

    /* 摘要：刻意弱化，与标题形成强对比 */
    .summary-text {
        color: var(--faint);
        font-family: "Noto Serif SC", "Songti SC", serif;
        font-size: 0.8rem;
        line-height: 2;
        font-weight: 400;
        margin-bottom: 0.5rem;
    }

    /* ── 侧栏 ──────────────────────────────────── */
    .side-list {
        display: flex;
        flex-direction: column;
        gap: 0.7rem;
    }

    .side-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.7rem;
        color: color-mix(in srgb, var(--text) 88%, transparent);
        font-size: 0.8rem;
    }

    .side-sub {
        color: var(--faint);
        font-size: 0.66rem;
        margin-left: 1rem;
        margin-top: 0.14rem;
    }

    .side-count {
        color: var(--gold);
        font-family: "Cormorant Garamond", Georgia, serif;
        font-size: 0.86rem;
        font-weight: 500;
        white-space: nowrap;
        padding-top: 0.05rem;
    }

    .side-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
        background: var(--green);
        box-shadow: 0 0 0 4px rgba(76, 191, 160, 0.09);
    }

    .side-dot.lagging {
        background: #d8b45e;
        box-shadow: 0 0 0 4px rgba(216, 180, 94, 0.09);
    }

    .side-dot.idle {
        background: var(--gold);
        box-shadow: 0 0 0 4px rgba(201, 168, 106, 0.09);
    }

    .mono-note {
        color: var(--muted);
        font-size: 0.76rem;
        line-height: 1.75;
    }

    .topic-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
    }

    .topic-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid rgba(201, 168, 106, 0.2);
        color: color-mix(in srgb, var(--text) 86%, transparent);
        border-radius: 999px;
        padding: 0.22rem 0.58rem;
        font-size: 0.7rem;
    }

    .topic-chip strong {
        color: var(--gold-bright);
        font-family: "Cormorant Garamond", Georgia, serif;
        font-weight: 600;
    }

    .feed-link {
        color: var(--gold-bright);
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        padding: 0.1rem 0.45rem;
        border-radius: 999px;
        border: 1px solid rgba(201, 168, 106, 0.25);
        background: rgba(201, 168, 106, 0.07);
        font-size: 0.68rem;
        margin-left: 0.5em;
        vertical-align: middle;
        white-space: nowrap;
    }

    .feed-link:hover {
        color: #f0d9a8;
        border-color: rgba(201, 168, 106, 0.45);
        background: rgba(201, 168, 106, 0.13);
    }

    /* ── 统计面板 ──────────────────────────────── */
    .stat-panel {
        min-height: 52px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.7rem 0.95rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        gap: 0.3rem;
    }

    .stat-label {
        color: var(--faint);
        font-size: 0.72rem;
        font-weight: 500;
        margin-bottom: 0;
        text-align: left;
        letter-spacing: 0.06em;
    }

    .stat-value {
        color: var(--gold-bright);
        font-family: "Cormorant Garamond", Georgia, serif;
        font-size: 1.3rem;
        line-height: 1;
        font-weight: 500;
        text-align: left;
    }

    /* ── Streamlit 原生控件暗色化 ──────────────── */
    div[data-testid="stButton"] button {
        border-radius: 10px;
        border: 1px solid rgba(201, 168, 106, 0.45);
        background: linear-gradient(180deg, #d9b877, #b58f4e);
        color: #14100a;
        font-weight: 500;
        min-height: 3rem;
        margin-top: 0;
        width: 100%;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    div[data-testid="stButton"] button:hover {
        border-color: rgba(224, 194, 138, 0.7);
        background: linear-gradient(180deg, #e6c683, #c19a58);
        color: #0e0b06;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stNumberInput"] input {
        background: rgba(255, 255, 255, 0.045);
        border-color: var(--line);
        color: var(--text);
        min-height: 3rem;
        border-radius: 10px;
    }

    div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 0.2rem 0.55rem;
        margin-right: 0.35rem;
        min-height: 34px;
        color: var(--muted);
    }

    div[data-testid="stRadio"] label:has(input:checked) {
        border-color: rgba(201, 168, 106, 0.55);
        background: rgba(201, 168, 106, 0.12);
        box-shadow: inset 0 0 0 1px rgba(201, 168, 106, 0.18);
        color: var(--gold-bright);
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stToggle"] label {
        color: var(--muted);
        font-size: 0.74rem;
        min-height: 1.1rem;
        margin-bottom: 0.32rem;
        display: block;
    }

    div[data-testid="stColumn"] > div:has(.stat-panel) {
        padding-top: 0.1rem;
    }

    div[data-testid="stColumn"] > div:has(> div[data-testid="stButton"]),
    div[data-testid="stColumn"] > div:has(> div[data-testid="stToggle"]),
    div[data-testid="stColumn"] > div:has(> div[data-testid="stSelectbox"]) {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }

    [data-testid="stExpander"] {
        background: linear-gradient(180deg, rgba(22, 27, 35, 0.92), rgba(16, 20, 27, 0.88));
        border: 1px solid rgba(201, 168, 106, 0.16);
        border-radius: 0 0 16px 16px;
        margin-bottom: 0;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        position: relative;
        z-index: 998;
        max-height: 62vh;
        overflow-y: auto;
        scrollbar-width: thin;
    }

    [data-testid="stExpander"] summary {
        padding: 0.82rem 0.95rem;
        color: var(--text);
        font-weight: 500;
        letter-spacing: 0.02em;
        position: sticky;
        top: 0;
        z-index: 1;
        background: linear-gradient(180deg, rgba(22, 27, 35, 0.97), rgba(16, 20, 27, 0.92));
    }

    [data-testid="stExpander"] summary:hover {
        background: rgba(201, 168, 106, 0.06);
    }

    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 0 0.95rem 0.85rem;
    }

    /* ── 响应式 ─────────────────────────────────── */
    @media (max-width: 900px) {
        .block-container {
            padding-top: 0.6rem;
            padding-left: 0.85rem;
            padding-right: 0.85rem;
        }

        .hero-bar {
            min-height: auto;
            padding: 0.95rem 0.9rem;
            margin-bottom: 0;
            flex-direction: column;
            align-items: flex-start;
        }

        .hero-left {
            min-width: 0;
        }

        .brand-title {
            font-size: 1.55rem;
            line-height: 1.55;
            padding-top: 0.18rem;
            padding-bottom: 0.18rem;
            min-height: 2.1em;
        }

        .brand-sub {
            letter-spacing: 0.26em;
        }

        .market-clock {
            font-size: 0.84rem;
            letter-spacing: 0.06em;
        }
    }

    @media (max-width: 640px) {
        .feed-layout {
            grid-template-columns: 48px 1fr;
            gap: 0.58rem;
        }

        .time-col {
            font-size: 0.66rem;
            padding-right: 0.56rem;
        }

        .time-main {
            font-size: 0.94rem;
        }

        .feed-title {
            font-size: 0.96rem;
            line-height: 1.58;
        }

        .summary-text {
            font-size: 0.76rem;
            line-height: 1.95;
        }

        .section-card {
            padding: 0.8rem;
            margin-bottom: 0.75rem;
        }

        .stat-panel {
            min-height: 46px;
            padding: 0 0.85rem;
        }

        div[data-testid="stButton"] button,
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            min-height: 2.7rem;
        }
    }
    </style>
    """
