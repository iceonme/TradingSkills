---
name: grid-rsi-strategy
description: A stateless, pure-function trading strategy that combines Dynamic Grid with RSI extreme filters and Market Regime detection.
---

# `grid-rsi-strategy` Skill 说明书

> 本 Skill 是一个极度纯净的“量化大脑”算法模块。它**没有任何网络访问能力**且**无状态**。所有的行情数据必须由外界（Runner/Arena）喂入，其职责仅仅是吐出标准的交易指令 (Signal)。

## 原理与特性 (Core Logic)
本策略脱胎于 `CTS1` 中的 `Dynamic Grid Strategy V4.0`，主要特性如下：
1. **动态网格 (Dynamic Grid)**: 根据近期 K 线高低点（N根 K 线内的 Max(High) 和 Min(Low) + Buffer）自动定位上下界，并划分对应的格数。
2. **RSI 自适应与过滤 (RSI Adaptive)**: 
   - 价格触发网格买入线时，若 RSI 处于极端超买状态，暂停买入（防接飞刀）。
   - 价格触发网格卖出线时，若 RSI 处于极端超卖状态，暂停卖出（防卖在地板）。

## 调用接口 (Usage for Runner / Agent)
这个策略作为一个标准的 Python 模块供 Runner 调用。不需要用命令行唤醒，而是直接在你的 Python 运行器中 `import` 使用：

```python
from skills.grid_rsi_strategy.core import analyze
from core.types import Kline, StrategyState

# 构建当前状态和最近的数据集 (至少包含策略所需要的周期数，如 100 根 K 线)
kline_list = [...] 
current_state = {
    "current_position_size": 0.5,
    "available_balance": 10000.0,
    "avg_entry_price": 60000.0  # (可选) 用于辅助判断盈利卖出
}

# 送入大脑计算
signals = analyze(kline_list, current_state)

# signals 会返回 List[Signal]，供你交给 execution skill 去执行
for sig in signals:
    print(sig)
```

## 输入数据要求 (Input Requirements)
策略引擎 `analyze` 需要至少过去 `60` 根 K 线（用于顺利算出 MA、ADX 趋势和 RSI）才能输出有意义的预判，推荐喂入 `100` 根。
数据必须符合 `core.types.Kline` 的数据结构。

## 可视化埋点 (Dashboard Binding)
由于计算时会产生 `grid_upper`, `grid_lower`, `rsi` 这样的专有指标，本策略自带一个 `dashboard_config.json`，供前端监控器将其画在 K 线图上。
