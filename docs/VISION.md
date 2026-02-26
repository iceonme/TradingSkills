# Trading Skills (TS) - 产品愿景 (Vision)

> **定位**: 跨平台的标准化交易策略与分析工具箱（基于开放协议）。  
> **白皮书组成**: [Vision](./VISION.md) | [Roadmap](./ROADMAP.md) | [Insights](./insights/) | [Collaboration Guide](./COLLABORATION_GUIDE.md)

---

## 一句话定位

**Trading Skills (TS)** 是一座去中心化的、专注于加密交易场景的“能力兵工厂”。它遵循 Anthropic 的 Skills 标准与 MCP (Model Context Protocol) 等开放协议，为任何遵循规范的 Agent 提供即插即用的交易策略、技术分析与舆情计算工具。

---

## 我们为什么需要独立的 Skills？

在过去，交易信号的计算逻辑（如：均线交叉、网格区间、MACD顶背离）往往与买卖执行引擎、账户管理代码死死地耦合在一起（如旧版的单体量化脚本）。

这导致了一个致命问题：**AI 智能体无法“拿来就用”。** 

一个基于提示词驱动的 PA (Personal Assistant) 想要知道现在是不是买点，它不需要理解复杂的 Python 矩阵运算，它只需要一个像人类使用计算器一样的标准接口：

```json
// Agent 的调用请求
{
  "name": "grid_rsi_analyzer",
  "arguments": {
    "symbol": "BTC-USDT",
    "timeframe": "15m"
  }
}

// Skill 的纯净返回
{
  "signal": "BUY",
  "confidence": 0.85,
  "reasoning": "RSI(32) touches the lower grid band (62000)."
}
```

## TS 的核心架构与开放性

1. **纯逻辑、无状态**：TS 里装着的一个个 Skill 就像数学公式，它们只接受数据输入，输出研判结论（买/卖/中性），**绝对不触碰用户的 API Key，也绝对不直接向交易所发单。**
2. **遵守 MCP/Anthropic 协议**：这意味着无论大模型底座是 Claude 3.5 还是未来的任意顶级模型，它们都能原生识别、注册并调用这些工具。
3. **服务于 TAS 与外部生态**：TS 生成的工具不仅是供 **Trading Agent Squad (TAS)** 里的技术分析员使用，也可以共享给整个 AI 交易社区。

## 远期愿景：Skill 创作者市场

TS 最终不仅是一个代码库，它的形态将演变为一个繁荣的 **Skills Market (技能插件市场)**：

- **量化工程师（Quants）**：利用高阶数学模型编写包含各种 Alpha 因子的 Skill 接口。
- **普通用户与 TAS 队长**：像是浏览 App Store 一样，订阅并为自己的技术分析员 Agent 安装最新的 "Whale Tracker Skill" 或是 "Dynamic Grid Strategy Skill"。
- **透明验证**：所有的 Skill 都可以被扔进 **Trading Agent Arena (TAA)** 里进行千锤百炼的回测，用真实的胜率数据为其定价。

---

**TS 库 - 武装你的 AI 交易员**
