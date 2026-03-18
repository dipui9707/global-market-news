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
        background: linear-gradient(180deg, color-mix(in srgb, var(--panel) 96%, white 4%), color-mix(in srgb, var(--panel-2) 96%, transparent));
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.05rem 1rem;
        margin-bottom: 0.8rem;
        overflow: visible;
        min-height: 104px;
        margin-top: 0.15rem;
    }

    .hero-left {
        min-width: 220px;
    }

    .brand-title {
        color: var(--gold);
        font-family: "Cormorant Garamond", serif;
        font-size: 1.78rem;
        line-height: 1.28;
        font-weight: 600;
        letter-spacing: 0.03em;
        padding-top: 0.12rem;
        padding-bottom: 0.08rem;
        white-space: nowrap;
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
    }

    div[data-testid="stMarkdown"]:has(.status-ribbon) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    .section-card {
        background: linear-gradient(180deg, color-mix(in srgb, var(--panel) 96%, white 4%), color-mix(in srgb, var(--panel-2) 96%, transparent));
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.9rem;
        margin-bottom: 0.9rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }

    .section-title {
        color: var(--gold);
        font-size: 0.92rem;
        margin-bottom: 0.6rem;
        letter-spacing: 0.08em;
    }

    .flash-list {
        margin: 0;
        padding-left: 1rem;
        color: var(--text);
    }

    .flash-list li {
        padding: 0.24rem 0;
        font-size: 0.95rem;
        border-bottom: 1px solid color-mix(in srgb, var(--line) 75%, transparent);
    }

    .flash-list li:last-child {
        border-bottom: none;
    }

    .feed-card {
        position: relative;
        border-top: 1px solid color-mix(in srgb, var(--line) 70%, transparent);
        padding: 0.62rem 0 0.66rem;
        margin-top: 0.08rem;
        transition: background 120ms ease;
    }

    .feed-card:hover {
        background: color-mix(in srgb, var(--gold-soft) 55%, transparent);
    }

    .feed-layout {
        display: grid;
        grid-template-columns: 68px 1fr;
        gap: 0.95rem;
        align-items: start;
    }

    .time-col {
        color: var(--muted);
        font-size: 0.76rem;
        text-align: right;
        padding-top: 0.15rem;
        border-right: 1px solid color-mix(in srgb, var(--line) 70%, transparent);
        padding-right: 0.9rem;
    }

    .time-main {
        color: color-mix(in srgb, var(--text) 78%, var(--muted));
        font-size: 1rem;
    }

    .feed-title {
        color: var(--text);
        font-family: "Cormorant Garamond", serif;
        font-size: 1.42rem;
        line-height: 1.02;
        margin: 0.02rem 0 0.22rem;
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
        font-size: 0.82rem;
        margin-bottom: 0.45rem;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin-bottom: 0.55rem;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        border: 1px solid color-mix(in srgb, var(--gold) 40%, transparent);
        background: color-mix(in srgb, var(--gold-soft) 90%, transparent);
        color: color-mix(in srgb, var(--gold) 85%, var(--text));
        border-radius: 999px;
        font-size: 0.72rem;
        padding: 0.14rem 0.46rem;
    }

    .badge.source {
        background: color-mix(in srgb, #7667e9 12%, transparent);
        border-color: color-mix(in srgb, #7667e9 28%, transparent);
        color: color-mix(in srgb, #7667e9 75%, var(--text));
    }

    .badge.duplicate {
        background: color-mix(in srgb, var(--red) 10%, transparent);
        border-color: color-mix(in srgb, var(--red) 28%, transparent);
        color: color-mix(in srgb, var(--red) 80%, var(--text));
    }

    .summary-text {
        color: color-mix(in srgb, var(--text) 84%, var(--muted));
        font-size: 0.85rem;
        line-height: 1.38;
        margin-bottom: 0.34rem;
    }

    .feed-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.5rem;
        color: var(--muted);
        font-size: 0.8rem;
    }

    .score-chip {
        color: var(--gold);
        font-size: 0.84rem;
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
        color: var(--gold);
        text-decoration: none;
    }

    .feed-link:hover {
        color: color-mix(in srgb, var(--gold) 70%, white 30%);
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
        padding: 0 0.95rem;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.015);
    }

    .stat-label {
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 500;
        margin-bottom: 0;
    }

    .stat-value {
        color: var(--text);
        font-size: 1.05rem;
        line-height: 1;
        font-family: "Noto Sans SC", sans-serif;
        font-weight: 700;
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
        align-items: center;
        padding-top: 0.1rem;
    }

    div[data-testid="stToggle"] label[data-testid="stWidgetLabel"] {
        display: none;
    }

    div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
        margin-top: 0;
    }
    </style>
    """
