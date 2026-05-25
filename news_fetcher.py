from __future__ import annotations

from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import re
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


HTML_SOURCES: Dict[str, str] = {
    "同花顺": "https://news.10jqka.com.cn/",
    "东方财富": "https://finance.eastmoney.com/",
}


USER_AGENT = "Mozilla/5.0 (compatible; StockAlertSystem/1.0)"


class AnchorNewsParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.results: List[Tuple[str, str]] = []
        self._current_href: Optional[str] = None
        self._text_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = dict(attrs)
        href = (attr_map.get("href") or "").strip()
        if not href:
            return
        self._current_href = href
        self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None and data:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current_href is None:
            return
        text = "".join(self._text_parts).strip()
        href = self._current_href.strip()
        self._current_href = None
        self._text_parts = []

        if not text or len(text) < 6:
            return
        if href.startswith("javascript:"):
            return

        full_link = urljoin(self.base_url, href)
        self.results.append((text, full_link))


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


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).strip().lower()


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


def fetch_html_news(source: str, url: str, timeout: int = 15, limit: int = 10) -> List[NewsItem]:
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        parser = AnchorNewsParser(base_url=url)
        parser.feed(html)
        parser.close()

        candidates = parser.results
        if len(candidates) < limit:
            # regex 作为兜底
            regex_results = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, flags=re.I | re.S)
            for href, raw_text in regex_results:
                text = re.sub(r"<[^>]+>", "", raw_text)
                text = " ".join(text.split()).strip()
                if len(text) >= 6:
                    candidates.append((text, urljoin(url, href.strip())))

        dedup_seen = set()
        picked: List[NewsItem] = []
        for title, link in candidates:
            key = (_normalize_text(title), link.strip())
            if key in dedup_seen:
                continue
            dedup_seen.add(key)
            picked.append(NewsItem(source=source, title=title.strip(), link=link.strip(), published="", summary=""))
            if len(picked) >= limit:
                break

        print(f"[HTML调试] {source} 抓取数量: {len(picked)}")
        return picked
    except Exception as exc:
        print(f"[HTML warning] {source} HTML抓取失败: {exc}")
        return []


def fetch_all_news() -> List[NewsItem]:
    all_items: List[NewsItem] = []
    for source, url in RSS_SOURCES.items():
        try:
            all_items.extend(fetch_rss(source, url))
        except Exception as exc:
            print(f"[RSS调试] {source} 抓取失败: {exc}")
            continue

    for source, url in HTML_SOURCES.items():
        items = fetch_html_news(source, url, limit=10)
        all_items.extend(items)

    # RSS + HTML 统一去重（按标准化标题 + 链接）
    merged: List[NewsItem] = []
    seen = set()
    for item in all_items:
        key = (_normalize_text(item.title), item.link.strip())
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)

    merged.sort(key=lambda x: x.published, reverse=True)
    return merged
