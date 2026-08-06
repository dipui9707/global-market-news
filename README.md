# Global Market News — 金融资讯聚合看板

Python + Streamlit 实现的**研究导向**金融资讯信息流看板，面向宏观跟踪、商品期货研究、
市场监测与投资研究工作流。界面为**暗色高级风格**（衬线字体、金色点缀、固定顶栏），
支持多源聚合、自动抓取、标题中文翻译与多维度筛选。

## 功能特性

- **21 个新闻源聚合**：宏观/媒体、AI 产业、商品期货、加密四大赛道（见下文来源列表）
- **每 5 分钟自动抓取**：服务器 cron 驱动 `scripts/run_pipeline.py`，含清洗、去重、打标、摘要、翻译、入库全流程
- **标题中文翻译**：DeepL API（Free 版每月 50 万字符），翻译按预算分批补足
- **暗色高级 UI**：深墨蓝背景 + 金色点缀、Noto Serif SC 衬线正文、Cormorant Garamond 数字、固定顶栏（品牌 + 时钟 + 筛选栏）
- **研究导向信息流**：来源/主题/区域/搜索筛选、重复报道折叠、`加载更多` 历史浏览、来源状态与热门话题侧栏
- **中文界面**：标题翻译为中文，摘要保留原文语言

## 项目结构

```text
global-market-news/
├─ data/                        # SQLite 数据库与缓存（不入库）
├─ scripts/
│  ├─ init_db.py                # 初始化数据库
│  └─ run_pipeline.py           # 抓取→清洗→去重→打标→摘要→翻译→入库
│  └─ run_mktnews_live_bridge.py# MktNews websocket 实时缓存桥（可选）
│  └─ run_translation_backfill.py
├─ src/news_mvp/
│  ├─ collectors/               # 各来源采集器（base/media_rss/mktnews/reuters/...）
│  ├─ dashboard/                # Streamlit UI（ui/components/styles/queries）
│  ├─ pipeline/                 # 数据管道（cleaning/dedup/tagging/scoring/translator/...）
│  ├─ config.py                 # 环境变量配置
│  ├─ db.py / schema.py         # 数据库访问与 schema
├─ .streamlit/config.toml       # Streamlit 主题（暗色）
├─ .env.example                 # 环境变量模板
├─ DEPLOYMENT.md                # 部署说明（本地/服务器/Docker/PaaS/cron）
├─ AGENTS.md                    # 开发原则
├─ PLANS.md                     # 开发计划
├─ pyproject.toml
└─ streamlit_app.py             # 入口
```

## 新闻源（21 个）

| 分类 | 来源 |
|------|------|
| 宏观/财经媒体 | Reuters、Bloomberg、CNBC、CNN、WSJ、FT、Yahoo Finance、Axios、MarketWatch |
| 官方机构 | Federal Reserve、BLS |
| 快讯/综合 | MktNews、Seeking Alpha、Investing.com Commodities、Google News 聚合（Reuters/BLS 经由） |
| AI 产业 | VentureBeat AI、TechCrunch AI |
| 商品期货 | OilPrice.com（能源/大宗）、Mining.com（金属/矿业）、The Western Producer（农产品）、FreightWaves（航运运价） |
| 加密 | CoinDesk |

> 数据管道设计保留了数据层能力（如 `importance_score` 字段），但 UI 层已移除重要性标签/排序与快讯面板，聚焦纯净信息流。

## 快速开始

```bash
git clone https://github.com/dipui9707/global-market-news.git
cd global-market-news
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env        # 编辑：TRANSLATION_ENABLED=true、TRANSLATION_API_KEY=<DeepL Key>
python scripts/init_db.py
python scripts/run_pipeline.py
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

完整部署（systemd / Docker / cron / PaaS）见 **[DEPLOYMENT.md](DEPLOYMENT.md)**。

## 数据管道

1. 采集 21 个来源的公开 RSS / API
2. 文本清洗与标准化（统一为 `ArticlePayload`）
3. URL、内容指纹、故事键三层去重
4. 规则打标（主题/资产标签）与轻量事件归组
5. 规则摘要生成
6. 标题 DeepL 中文翻译（按预算分批，`TRANSLATION_MAX_ITEMS_PER_RUN` 控制单次数量）
7. 入库 SQLite（WAL 模式，保留上限 `ARTICLE_RETENTION_COUNT`）

## 翻译

- 默认 **DeepL**（`TRANSLATION_PROVIDER=deepl`）：Free 版 `https://api-free.deepl.com/v2/translate`，Pro 版改 `https://api.deepl.com/v2/translate`
- 兼容 OpenAI 风格接口（`TRANSLATION_PROVIDER=openai` + `TRANSLATION_BASE_URL`，如 Qwen/DashScope），作为可选路径保留
- 仅翻译标题；摘要保留原文语言

## 配置

全部环境变量见 `.env.example` 与 DEPLOYMENT.md「配置项说明」。关键项：

| 配置项 | 说明 |
|--------|------|
| `TRANSLATION_ENABLED` / `TRANSLATION_API_KEY` | 标题翻译开关与 DeepL Key |
| `TRANSLATION_PROVIDER` | `deepl` 或 `openai`（兼容接口） |
| `COLLECTOR_ITEM_LIMIT` | 每源单次抓取上限 |
| `ARTICLE_RETENTION_COUNT` | 文章保留上限（默认 5000） |
| `DEFAULT_LOOKBACK_HOURS` | 看板默认时间窗口 |

## 已知限制

- Reuters / BLS 经 Google News RSS 中转；部分站点（Reuters、FT、WSJ）有反爬，抓取偶发 401/403
- 新闻原文均为国外站点，国内点击"原文"需自行解决网络访问
- 事件归组、重要性评分为规则式启发，非实体级
- 看板默认无认证，公网部署建议加反代认证
- 界面字体来自 Google Fonts CDN，国内加载可能缓慢，不影响功能

## 开发文档

- [AGENTS.md](AGENTS.md) — 架构与开发原则
- [PLANS.md](PLANS.md) — 开发阶段记录
