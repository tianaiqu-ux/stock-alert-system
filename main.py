from datetime import datetime

from news_fetcher import fetch_all_news
from report_generator import (
    build_morning_brief_cn,
    export_csv,
    export_markdown,
    summarize_by_source,
    top_titles,
)


def main() -> None:
    news_items = fetch_all_news()
    source_stats = summarize_by_source(news_items)
    top5 = top_titles(news_items, limit=5)
    brief = build_morning_brief_cn(news_items, source_stats, max_chars=200)

    print("=== 晨报摘要 ===")
    print(f"抓取时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"今日重要新闻总数: {len(news_items)}")
    print("分来源数量:")
    for source, count in source_stats.items():
        print(f"- {source}: {count}")

    print("Top5 标题:")
    for idx, title in enumerate(top5, start=1):
        print(f"{idx}. {title}")

    print("\n约200字中文晨报:")
    print(brief)

    md_path = export_markdown(news_items, source_stats, top5, brief)
    csv_path = export_csv(news_items)

    print("\n已保存文件:")
    print(f"- {md_path}")
    print(f"- {csv_path}")


if __name__ == "__main__":
    main()
