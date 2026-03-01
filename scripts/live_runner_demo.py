import os
import sys
import json
import time

# 修复 Windows 的表情符号输出编码问题
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 添加 TradingSkills 根目录到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
ts_root = os.path.dirname(script_dir)
sys.path.insert(0, ts_root)

# 导入两大“卡带”：数据卡带、策略卡带
from skills.okx_kline_feed.core import fetch_klines
from skills.grid_rsi_strategy.core import analyze
from core.types import StrategyState

def run_demo():
    print("🚀 [Runner] 正在启动 TS 游戏机原型...")
    time.sleep(1)
    
    symbol = "BTC-USDT"
    print(f"📡 [Data Feed] 正在唤醒数据感知 Skill 拉取 {symbol} 最新 K 线...")
    try:
        # 步骤 1: 使用数据卡带拉取数据
        klines = fetch_klines(symbol=symbol, bar="15m", limit=150)
        print(f"✅ [Data Feed] 成功获取 {len(klines)} 根历史 K 线数据。")
    except Exception as e:
        print(f"❌ [Data Feed] 数据抓取失败: {e}")
        return

    # 构造假定的当前系统状态 (在真正的实盘 Runner 里，这里会去调用 Execution Skill 查持仓)
    current_state: StrategyState = {
        "current_position_size": 0.0,
        "available_balance": 10000.0,
        "avg_entry_price": None
    }
    
    print("\n🧠 [Strategy] 正在唤醒 grid_rsi_strategy 计算信号...")
    print(f"   [Strategy] 喂入前提状态: 持仓 {current_state['current_position_size']}, 余额 {current_state['available_balance']}")
    
    # 步骤 2: 将数据和状态喂入策略大模型进行计算
    try:
        signals = analyze(klines, current_state, symbol=symbol)
    except Exception as e:
        print(f"❌ [Strategy] 策略引擎计算崩溃: {e}")
        return
        
    print("\n🎯 [Orchestrator] 运算结束，策略输出指令如下:")
    for sig in signals:
        action = sig.get('action')
        metadata = sig.get('metadata', {})
        print("-" * 50)
        print(f"🔹 指令类型 : {action}")
        print(f"🔹 交易标的 : {sig.get('symbol')}")
        print(f"🔹 期望数量 : {sig.get('amount')}")
        
        # 打印扩展日志（用于喂给前端 Dashboard 取色绘图）
        print("📊 [Dashboard 元数据]:")
        print(f"   - 当前 RSI   : {metadata.get('rsi', 0):.2f}")
        print(f"   - 网格上界   : {metadata.get('grid_upper', 0):.2f}")
        print(f"   - 网格下界   : {metadata.get('grid_lower', 0):.2f}")
        
        if action != "HOLD":
            print(f"🚀 [Orchestrator] ⚠️ 触发了交易指令 {action}！你可以将此 Signal 路由至 Execution Skill 进行实际发单。")
        else:
            print(f"⏳ [Orchestrator] 策略处于观望状态 (HOLD)，没有任何挂单动作。")
            

if __name__ == "__main__":
    run_demo()
