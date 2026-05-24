from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from news_fetcher import NewsItem


OUTPUT_DIR = Path("outputs")


def summarize_by_source(news: List[NewsItem]) -> Dict[str, int]:
    return dict(Counter(item.source for item in news))


def top_titles(news: List[NewsItem], limit: int = 5) -> List[str]:
    return [item.title for item in news[:limit]]


def build_morning_brief_cn(news: List[NewsItem], source_stats: Dict[str, int], max_chars: int = 200) -> str:
    if not news:
        return "今日未抓取到有效财经新闻，请稍后重试。"

    hot_titles = "；".join(item.title for item in news[:3])
    source_text = "，".join(f"{k}{v}条" for k, v in source_stats.items())

    text = (
        f"今晨共筛选出{len(news)}条重点财经新闻，来源包括{source_text}。"
        f"市场关注点集中在：{hot_titles}。"
        "整体来看，全球市场仍围绕增长预期、通胀路径与政策信号展开博弈，"
        "建议重点跟踪宏观数据与龙头公司指引变化。"
    )

    return text[:max_chars]


def export_markdown(news: List[NewsItem], source_stats: Dict[str, int], top5: List[str], brief: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"morning_report_{ts}.md"

    lines = [
        "# 财经晨报",
        "",
        f"- 生成时间(UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 重要新闻数量: {len(news)}",
        "",
        "## 来源统计",
    ]
    for source, count in source_stats.items():
        lines.append(f"- {source}: {count}")

    lines.extend(["", "## Top5 标题"])
    for i, title in enumerate(top5, start=1):
        lines.append(f"{i}. {title}")

    lines.extend(["", "## 200字中文晨报", brief, "", "## 明细"])
    for item in news:
        lines.append(f"- **[{item.source}]** {item.title}")
        if item.link:
            lines.append(f"  - 链接: {item.link}")
        if item.published:
            lines.append(f"  - 时间: {item.published}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def export_csv(news: List[NewsItem]) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"morning_report_{ts}.csv"

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["source", "title", "published", "link", "summary"],
        )
        writer.writeheader()
        for n in news:
            writer.writerow(
                {
                    "source": n.source,
                    "title": n.title,
                    "published": n.published,
                    "link": n.link,
                    "summary": n.summary,
                }
            )

    return str(path)
