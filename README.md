# Stock Alert System - 财经晨报生成器（零依赖版本）

一个可直接运行的 Python 项目：自动抓取 Bloomberg / Reuters / WSJ 公共 RSS，分析并生成中文晨报，同时导出 Markdown 和 CSV。

## 功能

- **零第三方依赖**：仅使用 Python 标准库（`urllib.request`、`xml.etree.ElementTree`、`csv` 等）
- 抓取来源：Bloomberg / Reuters / WSJ
- 控制台输出：
  - 今日重要新闻总数
  - 分来源数量
  - Top5 标题
  - 约200字中文晨报
- 保存 Markdown 报告
- 保存 CSV 报告

## 安装

无需安装第三方依赖。

## 运行

```bash
python main.py
```

运行后会在 `outputs/` 下生成：

- `morning_report_*.md`
- `morning_report_*.csv`

## 文件说明

- `main.py`：主程序入口
- `news_fetcher.py`：RSS 抓取与解析（标准库实现）
- `report_generator.py`：统计与报告导出（Markdown + CSV）
- `config.yaml`：配置示例
- `requirements.txt`：依赖说明（零依赖）
