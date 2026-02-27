# ADR-001: CTS1 核心能力剥离与 Skill 化解耦设计

> **状态**: 🟢 ACCEPTED
> **日期**: 2026-02-28

## 1. 背景与目标
原有的 `CTS1` 交易项目代码存在较强的功能耦合。为了符合最新的 `TA` 架构（特别是 `TradingSkills` 的 Anthropic Skills 标准），我们需要将“交易执行”和“网格策略”等核心逻辑剥离为独立的、标准化的 Skill 工具，彻底实现“逻辑算法”、“外部执行”和“可视化前端”解耦协同。

## 2. 架构设计决策

我们将重点在 `TradingSkills` 目录下构建标准的 AgentSkills 体系。

### 2.1 交易执行网关 (trading_exe)
- **定位**: 底层动作执行器（无状态的手臂）。
- **设计模式**: 采用适配器与驱动/提供者架构 (Adapter Pattern)。
  - 对外暴露统一的 Anthropic Tool 调用接口（如 `get_positions`, `place_order`）。
  - 对内实例化不同环境的 Providers（如 `OKXProvider`, `BinanceProvider` 等）。
- **规范要求**: 每个 Skill 文件夹下**强制**包含标准 `SKILL.md` 指令说明和用于 Agent 统一切入的命令行网关 `scripts/execute.py`。

### 2.2 网格交易策略分析器 (grid_rsi)
- **定位**: 纯粹无状态的分析与决策引擎。
- **职责剥离**: 
  - 严禁策略代码直接调用交易所 API 发送真实订单；
  - 它仅接收 K 线、资金等标准输入数据；
  - 计算分析后，输出标准化的结构化 `Signal` 交易指令（如：买/卖，数量，价格边界），再交由 Runner 或外层 Agent 调用下游工具执行。

### 2.3 可视化前端大屏的剥离 (Dashboard)
- **定位**: 独立的监控与复盘观察者模块 (Observer/Monitor)。
- **规则要求**: 任何底层的 `trading_exe` 或是 `grid_rsi` 策略中**严禁**包含和混杂任何图表渲染与数据推送的前端逻辑。
- **数据流解耦**: 执行流或策略一旦产生动作数据，仅通过**状态持久化落盘结构数据（文件/JSON）**或发送至**轻权重消息总线（Redis队列/轮询API）**向外部广播。Dashboard 作为观察者去读取日志自行绘制 K 线和交易点位。

### 2.4 TS 策略驱动型接口标准 (Trading Strategy Interface Protocol)
为了确保策略的高度复用与跨环境的绝对安全（实盘/回测无缝切换），所有策略 Skill 必须遵守这套内部的 **接口依赖注入机制**：

1. **接口盲插 (Plug and Play)**:
   - 策略引擎本身**不允许**写死任何类似 `requests.get('okx.com')` 的网络获取代码。
   - 策略必须只识别抽象的 `DataFeed` (数据接收器) 和 `Executor` (操作手柄) 接口。

2. **数据接收接口设计的灵活性 (Flexible DataFeed)**:
   - 由于不同策略所需的数据源千奇百怪（K线、链上、情绪等），**强制对所有 `DataFeed` 输入格式进行大一统是不现实也是没有必要的**。
   - **设计规范**: `DataFeed` 应该只是一个**宽泛的接收器接口定义**（或者包含元数据的流式口）。策略只需要声明“我期待什么结构的数据戳到这个接收器上”，宿主（环境）或者负责给它喂数据的大脑（PA）只需照着这个特定策略期待的格式扔进接收器即可。

3. **执行指令的严格标准化**:
   - 相比于输入数据的千奇百怪，**输出的交易指令必须被严格标准化**。
   - 策略计算结束后，可以交给 PA (Personal Assistant) 做进一步的二次分析判断，也可以直接扔给 `Trading Executor`。无论是谁接手，指令的形态都必须遵循标准协议（如明确的 Side, Amount, Symbol 等）。

### 2.5 策略驱动架构图解

```mermaid
graph TD
    %% ----- 样式设定 -----
    classDef interface fill:#f9f,stroke:#333,stroke-width:2px;
    classDef skill fill:#fff,stroke:#e6e6e6,stroke-width:2px;
    classDef impl fill:#bbf,stroke:#333,stroke-width:1px;
    
    %% ----- 核心：策略 Skill 模型 -----
    subgraph Trading_Skill ["Trading Strategy Skill (遵循内部接口标准)"]
        direction TB
        
        %% 块1：输入层
        subgraph Layer_1 ["📥 数据接收器 (Data Feed Interface)"]
            IF_Data["宽泛的数据流口<br/>(按策略自定义所需元数据)"]
        
        %% 块2：计算层
        subgraph Layer_2 ["🧠 核心策略计算 (Strategy Logic)"]
            Engine("{ 千奇百怪的策略引擎 }<br/>(网格 / 均线 / 情绪)<br/>内部定时器或事件驱动")
        end
        
        %% 块3：输出层
        subgraph Layer_3 ["📤 指令输出接口 (Executor Interface)"]
            IF_Exec["输出标准操作<br/>(place_order, cancel_order)"]
        end
        
        %% 内部流转
        Layer_1 --> Engine
        Engine --> Layer_3
    end
    class Trading_Skill skill;
    class Layer_1,Layer_3 interface;
    
    %% ----- 外部：实盘连接示范 -----
    subgraph Env_Live ["实盘宿主 (Live Trading Host)"]
        Live_Data["Binance / OKX 数据流"]
        Live_Exe["Binance / OKX 下单API"]
    end
    class Live_Data,Live_Exe impl;
    
    %% ----- 外部：回测连接示范 -----
    subgraph Env_Backtest ["回测引擎宿主 (TAA Arena Host)"]
        CSV_Data["本地 CSV / Parquet 数据文件"]
        Mock_Exe["本地虚拟内存撮合账本"]
    end
    class CSV_Data,Mock_Exe impl;
    
    %% ----- 依赖注入的连接线 -----
    Live_Data ==>|"注入"| IF_Data
    CSV_Data -.->|"注入"| IF_Data
    
    IF_Exec ==>|"发单"| Live_Exe
    IF_Exec -.->|"发单"| Mock_Exe
```

## 3. 全局规范验证
所有的 AgentSkills 必须完全隔离职责，保证单点测试覆盖且能如拼图般随意接插不同引擎验证。
