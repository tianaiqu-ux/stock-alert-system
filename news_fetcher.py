from __future__ import annotations

from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Dict, List
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


@dataclass
class NewsItem:
    source: str
    title: str
    link: str
    published: str
    summary: str


RSS_SOURCES: Dict[str, str] = {
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
    "WSJ": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
}


USER_AGENT = "Mozilla/5.0 (compatible; StockAlertSystem/1.0)"


def _first_text(node: ET.Element, tags: List[str]) -> str:
    for tag in tags:
        found = node.find(tag)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def _parse_date(raw: str) -> str:
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).isoformat()
    except Exception:
        return raw.strip()


def fetch_rss(source: str, url: str, timeout: int = 15) -> List[NewsItem]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        status_code = getattr(resp, "status", None) or resp.getcode()
        content = resp.read()

    preview = content.decode("utf-8", errors="replace")[:200]
    print(f"[RSS调试] {source} 状态码: {status_code}")
    print(f"[RSS调试] {source} 内容前200字符: {preview}")

    root = ET.fromstring(content)
    items: List[NewsItem] = []

    for node in root.findall(".//item"):
        title = _first_text(node, ["title"])
        link = _first_text(node, ["link"])
        pub = _first_text(node, ["pubDate", "published", "updated"])
        desc = _first_text(node, ["description", "summary"])

        if title:
            items.append(
                NewsItem(
                    source=source,
                    title=title,
                    link=link,
                    published=_parse_date(pub),
                    summary=desc,
                )
            )

    print(f"[RSS调试] {source} 解析 item 数量: {len(items)}")
    return items


def fetch_all_news() -> List[NewsItem]:
    all_items: List[NewsItem] = []
    for source, url in RSS_SOURCES.items():
        try:
            all_items.extend(fetch_rss(source, url))
        except Exception as exc:
            print(f"[RSS调试] {source} 抓取失败: {exc}")
            continue

    all_items.sort(key=lambda x: x.published, reverse=True)
    return all_items
