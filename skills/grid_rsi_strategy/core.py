import pandas as pd
import numpy as np
import sys
import os
from enum import Enum
from typing import List, Tuple

# 将核心类型库引入（保证我们在包内外直接调用均可）
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from core.types import Kline, Signal, StrategyState, SignalAction

class MarketRegime(Enum):
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"

# 默认策略配置
DEFAULT_PARAMS = {
    'grid_refresh_period': 1440, # 网格刷新周期(以K线数为单位，对应原代码24h)
    'grid_buffer_pct': 0.005,    # 网格缓冲区 0.5%
    'rsi_period': 14,
    'ma_period': 200,            # 趋势过滤均线 200周期
    'adx_threshold': 25.0,
    'adaptive_rsi': True,
    'rsi_oversold': 30.0,
    'rsi_overbought': 70.0,
    'rsi_extreme_buy': 80.0,     # 禁止极端超买接盘
    'rsi_extreme_sell': 20.0,    # 禁止极端超卖割肉
    'rsi_weight': 1.0,           # RSI对网格偏移的影响权重
    'max_positions': 5,          # 最大开仓层数
    'base_amount': 0.01          # 每次基础买入手数
}

def _calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0

def _calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int=14) -> float:
    if len(high) < period + 1:
        return 0.0
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    up = high.diff()
    down = -low.diff()
    
    pos_dm = pd.Series(np.where((up > down) & (up > 0), up, 0))
    neg_dm = pd.Series(np.where((down > up) & (down > 0), down, 0))
    
    atr = tr.rolling(window=period).mean()
    pos_di = (pos_dm.rolling(window=period).mean() / atr) * 100
    neg_di = (neg_dm.rolling(window=period).mean() / atr) * 100
    
    dx = (abs(pos_di - neg_di) / (pos_di + neg_di)) * 100
    adx = dx.rolling(window=period).mean()
    return adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0.0

def _detect_market_regime(df: pd.DataFrame, params: dict) -> Tuple[MarketRegime, float]:
    if len(df) < params['ma_period']:
        return MarketRegime.RANGING, 0.0
    adx = _calculate_adx(df['high'], df['low'], df['close'], period=14)
    ma = df['close'].rolling(window=params['ma_period']).mean().iloc[-1]
    current_price = df['close'].iloc[-1]
    
    if adx > params['adx_threshold']:
        if current_price > ma * 1.02:
            return MarketRegime.TRENDING_UP, adx
        elif current_price < ma * 0.98:
            return MarketRegime.TRENDING_DOWN, adx
    return MarketRegime.RANGING, adx

def _get_adaptive_rsi_thresholds(df: pd.DataFrame, params: dict) -> Tuple[float, float]:
    if not params['adaptive_rsi']:
        return params['rsi_oversold'], params['rsi_overbought']
    returns = df['close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(1440) 
    base_oversold = params['rsi_oversold']
    base_overbought = params['rsi_overbought']
    vol_factor = min(max(volatility / 0.5, 0.5), 2.0)
    
    adj_oversold = max(20, min(40, base_oversold / vol_factor))
    adj_overbought = min(80, max(60, 100 - (100 - base_overbought) / vol_factor))
    return adj_oversold, adj_overbought

def analyze(kline_list: List[Kline], current_state: StrategyState, symbol: str = "BTC-USDT") -> List[Signal]:
    """
    核心分析引擎
    输入: K线历史数组 (推荐前置提供 200+ 根，以便平滑计算均线), 当前持仓及资金状态
    输出: 动作指令数组 Signal
    """
    signals = []
    
    if len(kline_list) < 2:
        return signals # 数据过少，不作操作
        
    df = pd.DataFrame(kline_list)
    # 取最后一根 K 线当作当前切面
    current_idx = -1
    prev_idx = -2
    
    current_low = df['low'].iloc[current_idx]
    current_high = df['high'].iloc[current_idx]
    current_price = df['close'].iloc[current_idx]
    
    # 提取过去配置窗口作为网格扫描
    lookback = min(DEFAULT_PARAMS['grid_refresh_period'], len(df))
    recent_data = df.iloc[-lookback:]
    recent_high = recent_data['high'].max()
    recent_low = recent_data['low'].min()
    
    range_size = recent_high - recent_low
    buffer = range_size * DEFAULT_PARAMS['grid_buffer_pct']
    
    # 基础网格边界
    upper = recent_high + buffer
    lower = recent_low - buffer
    
    # 指标计算
    rsi = _calculate_rsi(df['close'], DEFAULT_PARAMS['rsi_period'])
    oversold, overbought = _get_adaptive_rsi_thresholds(df, DEFAULT_PARAMS)
    
    # 计算 RSI 信号并调整偏移
    rsi_signal = 0.0
    if rsi > overbought:
        rsi_signal = -1.0
    elif rsi < oversold:
        rsi_signal = 1.0
        
    shift = range_size * rsi_signal * DEFAULT_PARAMS['rsi_weight'] * 0.2
    grid_upper = upper + shift
    grid_lower = lower + shift
    
    # 生成 Signal 数据并带扩展标注数据，用于外围可视化或监控
    metadata = {
        "rsi": float(rsi),
        "grid_upper": float(grid_upper),
        "grid_lower": float(grid_lower),
        "strategy": "grid-rsi-v4"
    }
    
    has_position = current_state['current_position_size'] > 0
    
    # 买入条件: 过去最低点在网格买线之上，当前最低点下穿了这根线 (插针捕捉)
    if df['low'].iloc[prev_idx] > grid_lower and current_low <= grid_lower:
        # RSI 极度超买不接盘规则
        if rsi < DEFAULT_PARAMS['rsi_extreme_buy']:
            signals.append({
                "action": "BUY",
                "symbol": symbol,
                "amount": DEFAULT_PARAMS['base_amount'],
                "price": None,
                "order_type": "MARKET", # 为了实盘简单，简化为市价吃单
                "metadata": {**metadata, "reason": "GRID_CROSS_LOWER"}
            })
            
    # 卖出条件: 过去最高点在网格之上之前，当前最高点穿透/突破网上界
    if df['high'].iloc[prev_idx] < grid_upper and current_high >= grid_upper:
        if has_position:
            avg_entry = current_state.get('avg_entry_price')
            if avg_entry and current_price >= avg_entry * 0.995: # 确保至少微弱盈利
                if rsi > DEFAULT_PARAMS['rsi_extreme_sell']:
                    signals.append({
                        "action": "SELL",
                        "symbol": symbol,
                        "amount": current_state['current_position_size'],
                        "price": None,
                        "order_type": "MARKET",
                        "metadata": {**metadata, "reason": "GRID_CROSS_UPPER"}
                    })
    
    # 无任何动作，返回带 metadata 的 HOLD 方便观测器拿走图表参数
    if not signals:
         signals.append({
            "action": "HOLD",
            "symbol": symbol,
            "amount": 0.0,
            "price": None,
            "order_type": "MARKET",
            "metadata": metadata
         })
         
    return signals
