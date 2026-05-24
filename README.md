# Stock Alert System - 财经晨报生成器

一个可直接运行的 Python 项目：自动抓取 Bloomberg / Reuters / WSJ 公共 RSS，分析并生成中文晨报，同时导出 Markdown 和 Excel。

## 功能

- 使用 `requests + xml.etree.ElementTree` 解析 RSS（不使用 `feedparser`）
- 抓取来源：Bloomberg / Reuters / WSJ
- 控制台输出：
  - 重要新闻数量
  - 来源统计
  - Top5 标题
  - 200字中文晨报
- 保存 Markdown 报告
- 保存 Excel 报告

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

运行后会在 `outputs/` 下生成：

- `morning_report_*.md`
- `morning_report_*.xlsx`

## 文件说明

- `main.py`：主程序入口
- `news_fetcher.py`：RSS 抓取与解析
- `report_generator.py`：统计与报告导出
- `config.yaml`：配置示例
- `requirements.txt`：依赖
