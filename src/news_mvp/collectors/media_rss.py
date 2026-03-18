from __future__ import annotations

import re

import requests

from news_mvp.collectors.base import normalize_title, utc_now_iso
from news_mvp.collectors.rss_multi import MultiFeedRSSCollector
from news_mvp.config import Settings


class BloombergCollector(MultiFeedRSSCollector):
    name = "bloomberg"
    source_name = "Bloomberg"
    feed_urls = (
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://feeds.bloomberg.com/politics/news.rss",
    )
    region = "Global"


class CNBCCollector(MultiFeedRSSCollector):
    name = "cnbc"
    source_name = "CNBC"
    feed_urls = (
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    )
    region = "United States"


class CNNCollector(MultiFeedRSSCollector):
    name = "cnn"
    source_name = "CNN"
    feed_urls = (
        "https://news.google.com/rss/search?q=site%3Acnn.com%20(markets%20OR%20economy%20OR%20business)%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen",
    )
    region = "Global"


class WSJCollector(MultiFeedRSSCollector):
    name = "wsj"
    source_name = "WSJ"
    feed_urls = (
        "https://news.google.com/rss/search?q=site%3Awsj.com%20(markets%20OR%20economy%20OR%20fed%20OR%20inflation)%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen",
    )
    region = "United States"


class FTCollector(MultiFeedRSSCollector):
    name = "ft"
    source_name = "FT"
    feed_urls = ("https://www.ft.com/rss/home/uk",)
    region = "Europe"


class YahooFinanceCollector(MultiFeedRSSCollector):
    name = "yahoo_finance"
    source_name = "Yahoo Finance"
    feed_urls = ("https://finance.yahoo.com/news/rssindex",)
    region = "Global"


class AxiosCollector(MultiFeedRSSCollector):
    name = "axios"
    source_name = "Axios"
    feed_urls = ("https://api.axios.com/feed/",)
    region = "United States"


class SCMPCollector(MultiFeedRSSCollector):
    name = "scmp"
    source_name = "SCMP"
    feed_urls = (
        "https://www.scmp.com/rss/91/feed",
        "https://www.scmp.com/rss/4/feed",
    )
    region = "China"


class ZaobaoCollector(MultiFeedRSSCollector):
    name = "zaobao"
    source_name = "联合早报"
    feed_urls = (
        "https://www.zaobao.com.sg/rss/china",
        "https://www.zaobao.com.sg/rss/finance",
    )
    region = "China"
    language = "zh"

    def collect(self, settings: Settings):
        items = super().collect(settings)
        if items:
            return items

        fetched_at = utc_now_iso()
        pattern = re.compile(
            r'<a[^>]+href="(?P<path>/[^"]*story\d+-\d+)"[^>]*><h2>(?P<title>.*?)</h2></a>',
            re.S,
        )
        seen_urls: set[str] = set()

        for url in ("https://www.zaobao.com.sg/finance", "https://www.zaobao.com.sg/news/china"):
            try:
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
                response.raise_for_status()
            except requests.RequestException:
                continue
            for match in pattern.finditer(response.text):
                path = match.group("path").strip()
                title = normalize_title(re.sub(r"<[^>]+>", "", match.group("title")).strip())
                full_url = f"https://www.zaobao.com.sg{path}"
                if not title or full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                items.append(
                    self._make_payload(
                        title=title,
                        url=full_url,
                        published_at=None,
                        fetched_at=fetched_at,
                        summary="",
                    )
                )
                if len(items) >= settings.collector_item_limit:
                    return items

        return items
