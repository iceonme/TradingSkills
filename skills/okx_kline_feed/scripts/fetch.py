import os
import sys
import argparse
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
skill_dir = os.path.dirname(script_dir)
sys.path.insert(0, skill_dir)

from core import fetch_klines

def main():
    parser = argparse.ArgumentParser(description="Data Feed Interface (TAS Standard)")
    parser.add_argument("--symbol", type=str, required=True, help="Trading pair, e.g. BTC-USDT")
    parser.add_argument("--bar", type=str, default="15m", help="Timeframe, e.g. 15m")
    parser.add_argument("--limit", type=int, default=100, help="Number of candles")
    
    args = parser.parse_args()
    
    try:
        klines = fetch_klines(symbol=args.symbol, bar=args.bar, limit=args.limit)
        print(json.dumps({"success": True, "count": len(klines), "data": klines}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
