# TradeMind 战术任务看板 (Tactical Board)

## 📋 联动机制 (Execution Hierarchy)

1. **Strategic (白皮书)**: [VISION](../VISION.md) / [ROADMAP](../ROADMAP.md) / [INSIGHTS](../insights/) —— 决定“为什么做”。
2. **Tactical (本看板)**: [BOARD.md](./BOARD.md) —— 管理当前的“核心战役”。
3. **Operational (执行层)**: 系统内置 `task.md` —— 具体的编码步骤。
4. **Memory (记忆层)**: [HANDOVER](../HANDOVER.md) (短期记忆) / [history/](./history/) (长期记忆)。

---

## 📅 PLAN (宏观规划 / 待办)
- [ ] **L2 通信社交协作层**: 多智能体消息总线、共识仲裁机制。
- [ ] **L3 经济信誉层**: Agent 激励系统、贡献度量化算法。
- [ ] **SaaS 模式扩展**: 云端运行节点 (Cloud Node) 与多租户隔离。
- [ ] **全年度回测 (2025)**: 建立全年的策略收益与回撤 Baseline。

---

## 🚀 TODO (当前进行中)
### 1. AAAgent 基座：八大模块构建层落地 [/]
> **目标**: 基于 [INS-002](../insights/INS-002-AAAgent-construction-layer-framework.md) 实现 AAAgent 核心底座。
- **技术设计**: [implementation_plan.md (Active)](../../.gemini/antigravity/brain/e0982473-282c-4b2e-aba0-03f118f34ad1/implementation_plan.md)
- [ ] 实现 `BaseAAAgent` 骨架、`Node` 接口与 `Channel` 适配原型
- [ ] 实现智能层核心 (SkillFactory / ReasoningSpec)
- [ ] 实现状态层原型 (Memory / Scheduler)
- [ ] 实现 L3 Feed 消息总线 (AAAgent 通信协议)

### 2. Team A 实战化与专属 Workspace [ ]
- [ ] 构建 PA 的 OODA 推理策略与 GridTool 双向增强
- [ ] 开发 Squad Workspace UI (Members / Feed / War Room)

### 3. CTS1 核心能力剥离与 Skill 化解耦 (TradingSkills) [/]
> **目标**: 将原单体脚本重构为符合 TS 接口协议的标准化 Skill，实现执行、策略、监控的三层解耦。
- **技术设计**: [ADR-001-System_Decoupling.md](../architecture/ADR-001-System_Decoupling.md)
- **阶段归档**: [2026-02-28_00-34_Extract_ADR.md](./history/2026-02-28_00-34_Extract_ADR.md)
- [x] 完成架构解耦设计与 TS 策略驱动型接口标准 (Interface Protocol)
- [x] 剥离 `okx_trading_exe` 为独立的适配器网关 Skill (DataFeed/Executor 接口)
- [x] 剥离 `grid_rsi` 为纯粹的无状态分析策略 Skill + 数据获取 Skill + 串联 Runner ([查看归档](./history/2026-03-01_15-45_Grid_Strategy_Refactor.md))
- [ ] 将可视化前端 Dashboard 剥离为独立的观察者模块

---

## ✅ DONE (已完成)
### v0.1 挑战赛 W2：分析层 Tools + LLM 单兵优化 (2026-02-21)
- **验证文档**: [history/2026-02-21_walkthrough.md](./history/2026-02-21_walkthrough.md)
- [x] 实现 RSI/SMA/MACD 分析工具
- [x] 实现 LLM Solo 三种情报深度变体 (Lite/Indicator/Strategy)
- [x] 成功运行 7 天密集回测验证
