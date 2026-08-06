# 部署说明

本项目是 **Python + Streamlit** 的金融资讯聚合看板。本文档覆盖从零开始部署的完整流程，
包括本地运行、服务器生产部署（systemd）、Docker，以及常见 PaaS 平台（Streamlit Cloud / Railway），
并说明定时抓取与翻译配置。

> 当前生产环境：Ubuntu 24.04 + Python 3.12 + Streamlit（systemd 服务，端口 8501）。
> 抓取与翻译：cron 每 5 分钟运行 `scripts/run_pipeline.py`；标题翻译使用 DeepL API。

---

## 1. 环境要求

| 项目 | 要求 |
|------|------|
| Python | ≥ 3.11（生产环境实测 3.12） |
| 网络 | 服务器需能直连国外新闻源与 DeepL API |
| 磁盘 | ≥ 1 GB（SQLite 数据库会随时间增长） |

## 2. 快速开始（本地 / 服务器）

```bash
# 1) 拉取代码
git clone https://github.com/dipui9707/global-market-news.git
cd global-market-news

# 2) 创建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 3) 配置环境变量（必做）
cp .env.example .env
#    编辑 .env，至少设置：TRANSLATION_ENABLED、TRANSLATION_API_KEY
#    （见第 4 节「配置项说明」）

# 4) 初始化数据库（首次）
python scripts/init_db.py
#    会创建 data/news_mvp.db 及全部数据表

# 5) 手动抓取一次数据
python scripts/run_pipeline.py

# 6) 启动看板
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
#    浏览器打开 http://<服务器IP>:8501
```

### 2.1 生产部署（systemd 服务）

以 root 创建 `/etc/systemd/system/news-dashboard.service`：

```ini
[Unit]
Description=Global Market News Dashboard
After=network.target

[Service]
WorkingDirectory=/root/global-market-news
ExecStart=/root/global-market-news/.venv/bin/streamlit run streamlit_app.py \
    --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=5
EnvironmentFile=/root/global-market-news/.env

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now news-dashboard.service
systemctl status news-dashboard.service      # 查看状态
journalctl -u news-dashboard.service -n 100  # 查看日志
```

## 3. 定时抓取

### 3.1 Linux cron（推荐，服务器自带持久磁盘）

```bash
crontab -e
# 每 5 分钟抓取一次（含翻译，按预算补足）
*/5 * * * * cd /root/global-market-news && .venv/bin/python scripts/run_pipeline.py >> logs/pipeline.log 2>&1
```

### 3.2 Docker + cron（容器内定时）

```bash
docker run -d --name gmn-pipeline \
  -v gmn-data:/app/data \
  --env-file .env \
  --restart always \
  your-image:latest \
  sh -c "python scripts/init_db.py && (crontab -l 2>/dev/null; echo '*/5 * * * * python scripts/run_pipeline.py >> logs/pipeline.log 2>&1') | crontab - && cron -f"
```

### 3.3 GitHub Actions（适合演示环境，注意 PaaS 磁盘限制见第 6 节）

```yaml
# .github/workflows/ingest.yml
name: ingest
on:
  schedule:
    - cron: "*/5 * * * *"
  workflow_dispatch: {}
jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e .
      - run: python scripts/init_db.py
      - run: python scripts/run_pipeline.py
        env:
          TRANSLATION_API_KEY: ${{ secrets.DEEPL_API_KEY }}
          TRANSLATION_ENABLED: "true"
          TRANSLATION_PROVIDER: deepl
```

> ⚠️ GitHub Actions / PaaS 平台文件系统是**临时**的：每次执行之间数据可能被清空，
> 仅适合演示或结合对象存储做持久化。**正式使用请部署到有持久磁盘的服务器 + cron**。

## 4. 配置项说明（.env）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `APP_ENV` | `development` | 运行环境标识 |
| `DATABASE_URL` | `sqlite:///data/news_mvp.db` | 数据库路径（相对项目根） |
| `STREAMLIT_SERVER_PORT` | `8501` | 看板端口 |
| `DEFAULT_LOOKBACK_HOURS` | `72` | 看板默认时间窗口（小时） |
| `DEFAULT_PAGE_SIZE` | `50` | 每页条数 |
| `COLLECTOR_ITEM_LIMIT` | `20` | 每个来源单次抓取条数上限 |
| `ARTICLE_RETENTION_COUNT` | `5000` | 数据库保留文章总数上限 |
| `AUTO_UPDATE_ENABLED` | `false` | 应用内自动刷新（一般用 cron 代替） |
| `AUTO_UPDATE_INTERVAL_SECONDS` | `300` | 自动刷新间隔 |
| `TRANSLATION_ENABLED` | `false` | 是否启用标题翻译 |
| `TRANSLATION_PROVIDER` | `deepl` | 翻译服务：`deepl` 或 OpenAI 兼容接口 |
| `TRANSLATION_API_KEY` | （空） | DeepL API Key（Free/Pro 均可） |
| `TRANSLATION_BASE_URL` | `https://api-free.deepl.com/v2/translate` | Free 版固定此地址；Pro 版改为 `https://api.deepl.com/v2/translate` |
| `TRANSLATION_SOURCE_LANG` | `auto` | 源语言（auto 自动检测） |
| `TRANSLATION_TARGET_LANG` | `ZH` | 目标语言（DeepL 用 `ZH` / `ZH-HANS`） |
| `TRANSLATION_MAX_ITEMS_PER_RUN` | `10` | 每次抓取最多翻译条数（控制额度） |
| `STORY_DEDUP_LOOKBACK_HOURS` | `36` | 故事聚合去重的回看窗口 |
| `MKTNEWS_LIVE_CACHE_PATH` | `data/mktnews_live_en.json` | MktNews 实时缓存文件 |
| `MKTNEWS_LIVE_CACHE_MAX_ITEMS` | `500` | 实时缓存最大条数 |

### DeepL 额度说明
- Free 版每月 **50 万字符**，按 `TRANSLATION_MAX_ITEMS_PER_RUN=10` 每 5 分钟抓取，
  月消耗远低于上限，一般无需调整；额度紧张可降到 `5`。
- 翻译按预算分批进行，`run_pipeline.py` 会每次补足未翻译的标题，无需手动干预。

## 5. 数据库

- 位置：`data/news_mvp.db`（SQLite 单文件）
- 备份：直接复制该文件即可，建议每日备份：
  ```bash
  0 3 * * * tar czf /root/backups/gmn-$(date +\%Y\%m\%d-\%H\%M).tar.gz -C /root/global-market-news data
  ```
- 恢复：停掉服务 → 用备份文件覆盖 `data/news_mvp.db` → 启动服务
- 迁移到新服务器：连同 `data/news_mvp.db` 一起拷贝即可保留全部历史数据

## 6. Docker 部署

仓库暂未内置 Dockerfile，可使用下面的示例（或按需调整）：

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY streamlit_app.py ./
COPY .streamlit ./.streamlit
RUN pip install --no-cache-dir -e . && mkdir -p data
EXPOSE 8501
CMD ["sh", "-c", "python scripts/init_db.py && streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]
```

```bash
docker build -t global-market-news .
docker run -d --name gmn -p 8501:8501 \
  -v gmn-data:/app/data --env-file .env global-market-news
```

> ⚠️ 容器/无状态平台（K8s、Railway、Vercel 等）的 `/app/data` 是临时卷，
> 重启即丢数据。**必须挂载持久卷**，否则只适合演示。

## 7. 常见问题

- **页面显示未来时间 / 时间偏移 7 小时**：老版本把无时区 RSS 时间当作服务器本地时区解析，
  已修复（按 UTC 处理）。若旧库有偏移数据，可对新源跑一次 pipeline 后人工核对。
- **字体加载慢或失败**：界面字体来自 Google Fonts CDN（`styles.py`），
  国内网络可能加载缓慢，不影响功能；如需离线可自行下载字体文件后本地引用。
- **点击"原文"国内打不开**：新闻源均为国外站点，需自行解决网络访问；
  曾内置服务器中转代理功能（已移除），如需要可重新启用。
- **抓取量少 / 某来源无数据**：部分站点有反爬（Reuters、FT、WSJ 等），
  偶尔 401/403 属正常，其他来源会正常补充；可查看 `logs/pipeline.log`。

## 8. 安全提醒

- `.env` 含 DeepL API Key 等敏感信息，**已加入 .gitignore，切勿提交或分享**。
- 数据库可能含未翻译的原文标题，公开部署前请评估内容合规性。
- 看板默认无认证，公网部署建议置于 nginx 反代 + 基本认证之后。
