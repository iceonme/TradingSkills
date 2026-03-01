import os
import sys
import requests
from typing import List, Optional
from datetime import datetime

# 将核心类型库引入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from core.types import Kline

def fetch_klines(symbol: str = "BTC-USDT", bar: str = "15m", limit: int = 100) -> List[Kline]:
    """
    拉取 OKX 历史 K 线并格式化为标准 TS Schema
    :param symbol: 交易对, 如 BTC-USDT
    :param bar: 时间周期, 如 1m, 15m, 1H, 1D
    :param limit: 获取条数, 默认 100, 最大 300
    :return: List[Kline] 按时间顺序排列好的K线数组 (从旧到新)
    """
    url = "https://www.okx.com/api/v5/market/candles"
    params = {
        "instId": symbol,
        "bar": bar,
        "limit": limit
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("code") != "0":
        raise Exception(f"OKX API Error: {data.get('msg')}")
        
    raw_klines = data.get("data", [])
    
    klines: List[Kline] = []
    # OKX 接口返回的数据是从新到旧的，我们需要将其反转为从旧到新的时序以便策略计算
    for candle in reversed(raw_klines):
        ts = int(candle[0])
        klines.append({
            "timestamp": ts,
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
            "datetime": datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return klines
