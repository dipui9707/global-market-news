from __future__ import annotations


def get_dashboard_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Noto+Sans+SC:wght@400;500;700&display=swap');

    :root {
        --bg: var(--background-color);
        --panel: color-mix(in srgb, var(--background-color) 82%, var(--secondary-background-color));
        --panel-2: color-mix(in srgb, var(--secondary-background-color) 92%, transparent);
        --line: color-mix(in srgb, var(--text-color) 14%, transparent);
        --text: var(--text-color);
        --muted: color-mix(in srgb, var(--text-color) 56%, var(--background-color));
        --gold: var(--primary-color);
        --gold-soft: color-mix(in srgb, var(--primary-color) 16%, transparent);
        --green: #2f9e78;
        --red: #cf5c66;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, color-mix(in srgb, var(--primary-color) 10%, transparent), transparent 28%),
            linear-gradient(
                180deg,
                color-mix(in srgb, var(--background-color) 96%, white 4%) 0%,
                color-mix(in srgb, var(--background-color) 92%, black 8%) 100%
            );
        color: var(--text);
        font-family: "Noto Sans SC", sans-serif;
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 1.2rem;
        max-width: 1400px;
    }

    .stMetric {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.4rem 0.7rem;
    }

    .terminal-shell {
        background: color-mix(in srgb, var(--panel) 88%, transparent);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 16px 40px rgba(0,0,0,0.10);
    }

    .hero-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        background:
            linear-gradient(135deg, color-mix(in srgb, var(--gold-soft) 22%, transparent), transparent 42%),
            linear-gradient(180deg, color-mix(in srgb, var(--panel) 97%, white 3%), color-mix(in srgb, var(--panel-2) 98%, transparent));
        border: 1px solid color-mix(in srgb, var(--gold) 18%, var(--line));
        border-radius: 16px;
        padding: 1.05rem 1rem;
        margin-bottom: 0.8rem;
        overflow: visible;
        min-height: 104px;
        margin-top: 0.15rem;
        box-shadow: 0 10px 28px color-mix(in srgb, var(--gold) 7%, transparent), inset 0 1px 0 rgba(255,255,255,0.32);
        position: relative;
    }

    .hero-bar::after {
        content: "";
        position: absolute;
        left: 1rem;
        right: 1rem;
        bottom: 0;
        height: 1px;
        background: linear-gradient(90deg, color-mix(in srgb, var(--gold) 55%, transparent), transparent 70%);
        opacity: 0.7;
    }

    .hero-left {
        min-width: 220px;
    }

    .brand-title {
        color: var(--gold);
        font-family: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
        font-size: 1.78rem;
        line-height: 1.65;
        font-weight: 600;
        letter-spacing: 0.01em;
        padding-top: 0.24rem;
        padding-bottom: 0.24rem;
        margin: 0;
        white-space: nowrap;
        overflow: visible;
        display: block;
        min-height: 2em;
    }

    .brand-sub {
        color: var(--muted);
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    .market-clock {
        color: var(--muted);
        font-size: 0.9rem;
        letter-spacing: 0.06em;
    }

    .control-bar {
        background: rgba(17,17,26,0.94);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.7rem 0.75rem 0.8rem;
        margin-bottom: 0.85rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.015);
    }

    .inline-kicker {
        color: var(--muted);
        font-size: 0.76rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .control-row-gap {
        height: 0.25rem;
    }

    .control-caption {
        color: var(--muted);
        font-size: 0.78rem;
        min-height: 1.15rem;
        margin-bottom: 0.32rem;
        display: flex;
        align-items: center;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .status-ribbon {
        color: var(--green);
        font-size: 0.88rem;
        padding: 0.2rem 0 0.55rem;
        letter-spacing: 0.01em;
    }

    div[data-testid="stMarkdown"]:has(.status-ribbon) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    .section-card {
        background:
            linear-gradient(180deg, color-mix(in srgb, var(--panel) 98%, white 2%), color-mix(in srgb, var(--panel-2) 98%, transparent));
        border: 1px solid color-mix(in srgb, var(--gold) 14%, var(--line));
        border-radius: 14px;
        padding: 0.9rem;
        margin-bottom: 0.9rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.16), 0 10px 24px rgba(0,0,0,0.04);
    }

    .mktnews-live-card {
        border-color: color-mix(in srgb, #4f6ea9 16%, var(--line));
        background:
            linear-gradient(180deg, color-mix(in srgb, #4f6ea9 6%, white 94%), color-mix(in srgb, var(--panel) 96%, white 4%));
    }

    .mktnews-live-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.45rem;
        color: color-mix(in srgb, var(--text) 92%, var(--muted));
        font-size: 0.82rem;
    }

    .section-title {
        color: var(--gold);
        font-size: 0.92rem;
        margin-bottom: 0.6rem;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .flash-section-card {
        background:
            linear-gradient(180deg, color-mix(in srgb, var(--gold-soft) 20%, white 80%), color-mix(in srgb, var(--panel) 96%, white 4%));
        border-color: color-mix(in srgb, var(--gold) 28%, var(--line));
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.28), 0 14px 28px rgba(88, 58, 25, 0.06);
        position: relative;
        overflow: hidden;
    }

    .flash-section-card::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, color-mix(in srgb, var(--gold) 92%, white 8%), color-mix(in srgb, #d88f2f 72%, transparent));
    }

    .flash-section-head {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 0.8rem;
        margin-bottom: 0.7rem;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid color-mix(in srgb, var(--gold) 16%, var(--line));
    }

    .flash-section-title {
        margin-bottom: 0;
        color: color-mix(in srgb, var(--gold) 92%, #8d5d14 8%);
        letter-spacing: 0.06em;
    }

    .flash-section-note {
        color: color-mix(in srgb, var(--text) 62%, var(--muted));
        font-size: 0.73rem;
        white-space: nowrap;
    }

    .flash-list {
        margin: 0;
        padding-left: 1.15rem;
        color: var(--text);
    }

    .flash-list li {
        padding: 0.56rem 0 0.62rem 0.26rem;
        font-size: 0.95rem;
        border-bottom: 1px solid color-mix(in srgb, var(--gold) 10%, var(--line));
        position: relative;
    }

    .flash-list li:last-child {
        border-bottom: none;
    }

    .flash-item::before {
        content: "";
        position: absolute;
        left: -0.88rem;
        top: 0.72rem;
        bottom: 0.74rem;
        width: 3px;
        border-radius: 999px;
        background: linear-gradient(180deg, color-mix(in srgb, var(--gold) 85%, white 15%), color-mix(in srgb, var(--gold) 35%, transparent));
        opacity: 0.9;
    }

    .flash-title {
        color: var(--text);
        font-weight: 700;
        line-height: 1.52;
    }

    .flash-meta {
        display: inline-flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.45rem;
        margin-left: 0.55rem;
    }

    .feed-card {
        position: relative;
        border-top: 1px solid color-mix(in srgb, var(--gold) 10%, var(--line));
        padding: 0.52rem 0.08rem 0.56rem 0.24rem;
        margin-top: 0.02rem;
        transition: background 120ms ease, transform 120ms ease, border-color 120ms ease;
        border-radius: 12px;
        background: color-mix(in srgb, var(--panel) 42%, transparent);
    }

    .feed-card:hover {
        background: linear-gradient(180deg, color-mix(in srgb, var(--gold-soft) 52%, white 48%), color-mix(in srgb, var(--panel) 92%, white 8%));
        transform: translateY(-1px);
        border-color: color-mix(in srgb, var(--gold) 30%, var(--line));
        box-shadow: 0 10px 24px rgba(88, 58, 25, 0.08), inset 0 1px 0 rgba(255,255,255,0.22);
    }

    .feed-card::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0.68rem;
        bottom: 0.68rem;
        width: 2px;
        border-radius: 999px;
        background: transparent;
        transition: background 120ms ease, opacity 120ms ease;
        opacity: 0;
    }

    .feed-card.priority-medium::before,
    .feed-card.priority-high::before {
        opacity: 1;
    }

    .feed-card.priority-medium::before {
        background: linear-gradient(180deg, color-mix(in srgb, var(--gold) 65%, white 12%), color-mix(in srgb, var(--gold) 28%, transparent));
    }

    .feed-card.priority-high::before {
        width: 3px;
        background: linear-gradient(180deg, color-mix(in srgb, var(--gold) 92%, white 8%), color-mix(in srgb, #cf9f42 68%, transparent));
    }

    .feed-layout {
        display: grid;
        grid-template-columns: 56px 1fr;
        gap: 0.78rem;
        align-items: start;
    }

    .time-col {
        color: var(--muted);
        font-size: 0.72rem;
        text-align: right;
        padding-top: 0.08rem;
        border-right: 1px solid color-mix(in srgb, var(--line) 70%, transparent);
        padding-right: 0.72rem;
    }

    .time-main {
        color: color-mix(in srgb, var(--text) 78%, var(--muted));
        font-size: 0.92rem;
    }

    .feed-title {
        color: var(--text);
        font-family: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
        font-size: 1.14rem;
        line-height: 1.24;
        font-weight: 700;
        margin: 0.02rem 0 0.16rem;
        letter-spacing: 0.005em;
    }

    .feed-title-zh {
        color: color-mix(in srgb, var(--gold) 90%, var(--text));
        font-size: 1rem;
        line-height: 1.25;
        margin: 0.05rem 0 0.18rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }

    .meta-line {
        color: var(--muted);
        font-size: 0.78rem;
        margin-bottom: 0.28rem;
        letter-spacing: 0.01em;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.28rem;
        margin-bottom: 0.36rem;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        border: 1px solid color-mix(in srgb, var(--gold) 32%, transparent);
        background: color-mix(in srgb, var(--gold-soft) 68%, white 32%);
        color: color-mix(in srgb, var(--gold) 85%, var(--text));
        border-radius: 999px;
        font-size: 0.68rem;
        padding: 0.1rem 0.38rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.18);
    }

    .badge.source {
        background: color-mix(in srgb, #4f6ea9 10%, white 90%);
        border-color: color-mix(in srgb, #4f6ea9 24%, transparent);
        color: color-mix(in srgb, #4f6ea9 82%, var(--text));
    }

    .badge.duplicate {
        background: color-mix(in srgb, var(--red) 8%, white 92%);
        border-color: color-mix(in srgb, var(--red) 28%, transparent);
        color: color-mix(in srgb, var(--red) 80%, var(--text));
    }

    .summary-text {
        color: color-mix(in srgb, var(--text) 84%, var(--muted));
        font-size: 0.8rem;
        line-height: 1.4;
        margin-bottom: 0.28rem;
    }

    .feed-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.5rem;
        color: var(--muted);
        font-size: 0.76rem;
    }

    .score-chip {
        color: color-mix(in srgb, var(--gold) 88%, var(--text));
        font-size: 0.74rem;
        border-radius: 999px;
        padding: 0.08rem 0.32rem;
        background: color-mix(in srgb, var(--gold-soft) 46%, white 54%);
        border: 1px solid color-mix(in srgb, var(--gold) 18%, transparent);
    }

    .side-list {
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
    }

    .side-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.7rem;
        color: color-mix(in srgb, var(--text) 92%, var(--muted));
        font-size: 0.88rem;
    }

    .side-sub {
        color: var(--muted);
        font-size: 0.72rem;
        margin-left: 1rem;
        margin-top: 0.14rem;
    }

    .side-count {
        color: color-mix(in srgb, var(--gold) 88%, var(--text));
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
        box-shadow: 0 0 0 4px rgba(119, 210, 187, 0.08);
    }

    .side-dot.lagging {
        background: #e2c26f;
        box-shadow: 0 0 0 4px rgba(226, 194, 111, 0.08);
    }

    .side-dot.idle {
        background: var(--gold);
        box-shadow: 0 0 0 4px rgba(194, 164, 107, 0.08);
    }

    .mono-note {
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.65;
    }

    .topic-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
    }

    .topic-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: color-mix(in srgb, var(--panel-2) 95%, white 5%);
        border: 1px solid color-mix(in srgb, var(--gold) 20%, transparent);
        color: color-mix(in srgb, var(--text) 88%, var(--muted));
        border-radius: 999px;
        padding: 0.2rem 0.55rem;
        font-size: 0.76rem;
    }

    .topic-chip strong {
        color: color-mix(in srgb, var(--gold) 88%, var(--text));
        font-weight: 700;
    }

    .feed-link {
        color: color-mix(in srgb, var(--gold) 88%, #8d6a26 12%);
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        padding: 0.1rem 0.42rem;
        border-radius: 999px;
        border: 1px solid color-mix(in srgb, var(--gold) 20%, transparent);
        background: color-mix(in srgb, var(--gold-soft) 38%, white 62%);
    }

    .feed-link:hover {
        color: color-mix(in srgb, var(--gold) 72%, #7b5a1c 28%);
        border-color: color-mix(in srgb, var(--gold) 36%, transparent);
        background: color-mix(in srgb, var(--gold-soft) 58%, white 42%);
    }

    .toolbar-note {
        color: var(--muted);
        font-size: 0.78rem;
        text-align: right;
        padding-top: 0.1rem;
        min-height: 1.35rem;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }

    .stat-panel {
        min-height: 48px;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 0.75rem 0.95rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.015);
        gap: 0.28rem;
    }

    .stat-label {
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 500;
        margin-bottom: 0;
        text-align: left;
    }

    .stat-value {
        color: var(--text);
        font-size: 1.05rem;
        line-height: 1;
        font-family: "Noto Sans SC", sans-serif;
        font-weight: 700;
        text-align: left;
    }

    .control-action-group {
        height: 0.35rem;
    }

    div[data-testid="stButton"] button {
        border-radius: 10px;
        border: 1px solid color-mix(in srgb, var(--gold) 38%, transparent);
        background: linear-gradient(180deg, color-mix(in srgb, var(--gold) 86%, white 14%), color-mix(in srgb, var(--gold) 84%, black 16%));
        color: color-mix(in srgb, var(--background-color) 30%, black 70%);
        font-weight: 700;
        min-height: 3rem;
        margin-top: 0;
        width: 100%;
        box-shadow: 0 8px 18px color-mix(in srgb, var(--gold) 18%, transparent);
    }

    div[data-testid="stButton"] button:hover {
        border-color: color-mix(in srgb, var(--gold) 60%, transparent);
        background: linear-gradient(180deg, color-mix(in srgb, var(--gold) 92%, white 8%), color-mix(in srgb, var(--gold) 80%, black 20%));
        color: color-mix(in srgb, var(--background-color) 20%, black 80%);
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stNumberInput"] input {
        background: color-mix(in srgb, var(--panel) 94%, white 6%);
        border-color: var(--line);
        color: var(--text);
        min-height: 3rem;
        border-radius: 10px;
    }

    div[data-testid="stRadio"] label {
        background: color-mix(in srgb, var(--panel) 94%, white 6%);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 0.2rem 0.55rem;
        margin-right: 0.35rem;
        min-height: 34px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.01);
    }

    div[data-testid="stRadio"] label:has(input:checked) {
        border-color: rgba(194, 164, 107, 0.42);
        background: rgba(194, 164, 107, 0.14);
        box-shadow: inset 0 0 0 1px rgba(194, 164, 107, 0.16);
        color: #f4e8c8;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stToggle"] label {
        color: var(--muted);
        font-size: 0.8rem;
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

    div[data-testid="stToggle"] {
        min-height: 3rem;
        display: flex;
        align-items: stretch;
        padding-top: 0.1rem;
        border: 1px solid color-mix(in srgb, var(--gold) 38%, transparent);
        border-radius: 10px;
        background: linear-gradient(180deg, color-mix(in srgb, var(--gold-soft) 55%, white 6%), color-mix(in srgb, var(--panel) 96%, transparent));
        padding-left: 0.85rem;
        padding-right: 0.85rem;
        box-shadow: 0 8px 18px color-mix(in srgb, var(--gold) 10%, transparent);
    }

    div[data-testid="stToggle"] > label {
        width: 100%;
        display: flex !important;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;
        margin-bottom: 0 !important;
        color: var(--text) !important;
        font-weight: 700;
        font-size: 0.95rem !important;
    }

    div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
        margin-top: 0;
    }

    details[data-testid="stExpander"] {
        background: linear-gradient(180deg, color-mix(in srgb, var(--panel) 96%, white 4%), color-mix(in srgb, var(--panel-2) 96%, transparent));
        border: 1px solid color-mix(in srgb, var(--gold) 16%, var(--line));
        border-radius: 14px;
        margin-bottom: 0.8rem;
        overflow: hidden;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.18);
    }

    details[data-testid="stExpander"] summary {
        padding: 0.78rem 0.95rem;
        color: var(--text);
        font-weight: 700;
        letter-spacing: 0.01em;
    }

    details[data-testid="stExpander"] summary:hover {
        background: color-mix(in srgb, var(--gold-soft) 35%, transparent);
    }

    details[data-testid="stExpander"] > div[role="region"] {
        padding: 0 0.95rem 0.85rem;
    }

    @media (max-width: 900px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 0.85rem;
            padding-right: 0.85rem;
        }

        .hero-bar {
            min-height: auto;
            padding: 0.9rem 0.85rem;
            margin-bottom: 0.6rem;
            flex-direction: column;
            align-items: flex-start;
        }

        .hero-left {
            min-width: 0;
        }

        .brand-title {
            font-size: 1.5rem;
            line-height: 1.7;
            padding-top: 0.22rem;
            padding-bottom: 0.22rem;
            min-height: 2.1em;
        }

        .brand-sub {
            letter-spacing: 0.16em;
        }

        .market-clock {
            font-size: 0.82rem;
            letter-spacing: 0.03em;
        }

        .status-ribbon {
            font-size: 0.82rem;
            padding-top: 0.05rem;
        }
    }

    @media (max-width: 640px) {
        .feed-layout {
            grid-template-columns: 46px 1fr;
            gap: 0.58rem;
        }

        .time-col {
            font-size: 0.68rem;
            padding-right: 0.52rem;
        }

        .time-main {
            font-size: 0.82rem;
        }

        .feed-title {
            font-size: 1.02rem;
            line-height: 1.16;
        }

        .meta-line,
        .summary-text,
        .feed-footer {
            font-size: 0.74rem;
        }

        .flash-list li {
            font-size: 0.88rem;
        }

        .flash-section-head {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.25rem;
        }

        .section-card {
            padding: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .stat-panel {
            min-height: 44px;
            padding: 0 0.8rem;
        }

        div[data-testid="stButton"] button,
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            min-height: 2.7rem;
        }
    }
    </style>
    """
