from typing import TypedDict, Literal, Optional, List, Any

# 动作类型：买入、卖出还是保持观望
SignalAction = Literal["BUY", "SELL", "HOLD"]

# 订单类型：市价单还是限价单
OrderType = Literal["MARKET", "LIMIT"]

class Kline(TypedDict):
    """
    标准的 OHLCV 字典，代表一根 K 线数据。
    无论是实盘还是回测，数据抓取卡带必须保证吐出的形式符合该规范。
    """
    timestamp: int      # 毫秒级时间戳，如 1672531200000
    open: float         # 开盘价
    high: float         # 最高价
    low: float          # 最低价
    close: float        # 收盘价
    volume: float       # 交易量
    datetime: Optional[str] # 便于阅读的字符串时间 "2023-01-01 00:00:00"

class Signal(TypedDict):
    """
    策略分析后吐出的标准“动作指令卡”。
    执行网关（Exe Skill）只负责按此指令发往交易所。
    """
    action: SignalAction    # BUY / SELL / HOLD
    symbol: str             # 交易对，如 'BTC-USDT'
    amount: float           # 下单数量 (如为空，如果是卖出可能是全卖或者特定的配置比例)，这里为了简化要求明确绝对值
    price: Optional[float]  # 仅限价单时有效
    order_type: OrderType   # MARKET / LIMIT
    metadata: Optional[dict[str, Any]] # 选填：透传一些排错信息或者策略的自信评分，不参与实际交易决策，如 "reason": "RSI_OVERSOLD"

class StrategyState(TypedDict):
    """
    由 Runner (游戏机) 每帧传递给策略的环境快照。
    由于策略纯无状态不可触网，策略依靠此状态判断例如:余额不够就不买。
    """
    current_position_size: float # 当前某交易对持仓量
    available_balance: float     # U本位可用余额
    avg_entry_price: Optional[float] # 当前持仓账户的平均入场价（用于判断是否盈利卖出）
