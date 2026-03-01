---
name: okx-kline-feed
description: A pure Data Feed Skill that fetches historical OHLCV (Kline) data from OKX and normalizes it into the TS Standard Kline schema.
---

# `okx-kline-feed` Skill 说明书

> 本 Skill 充当外界交易所的“眼睛”。它只做一件事情：去 OKX 交易所把原始的 K 线数据下载下来，并清洗成我们体系内标准承认的字典格式，绝不携带任何情绪或者计算算法。

## 调取接口 (Usage)
如果是供外部 Agent 使用命令行调用以获取本地 JSON 文件快照：
```bash
python scripts/fetch.py --symbol BTC-USDT --bar 15m --limit 100
```
如果是作为内部模块供 `Runner` 调用：
```python
from skills.okx_kline_feed.core import fetch_klines

# 返回标准的 List[Kline] 结构
klines = fetch_klines(symbol="BTC-USDT", bar="15m", limit=100)
```
