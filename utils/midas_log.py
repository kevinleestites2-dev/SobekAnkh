"""
Sobek Ankh — MidasPrime Integration
Every trade logged to the War Chest in real time.

v2.0 — Enhanced trade logging:
- Strategy name, entry price, exit price, PnL, win/loss outcome, timestamp
- Per-strategy statistics tracking
- AI Intelligence Layer integration
"""
import os
import json
import time
from datetime import datetime
from collections import defaultdict

LOG_FILE = "logs/war_chest.json"
TRADE_LOG = "logs/trades.jsonl"
STRATEGY_STATS_FILE = "logs/strategy_stats.json"

def log_trade(trade: dict):
    """Log trade to JSONL file and update war chest summary."""
    os.makedirs("logs", exist_ok=True)
    
    trade["logged_at"] = datetime.utcnow().isoformat()
    
    if "strategy" not in trade:
        trade["strategy"] = "unknown"
    if "entry" not in trade:
        trade["entry"] = 0.0
    if "exit" not in trade:
        trade["exit"] = 0.0
    if "pnl" not in trade:
        trade["pnl"] = 0.0
    
    trade["outcome"] = "WIN" if trade["pnl"] > 0 else "LOSS" if trade["pnl"] < 0 else "BREAK_EVEN"
    
    if "timestamp" not in trade:
        trade["timestamp"] = time.time()
    
    with open(TRADE_LOG, "a") as f:
        f.write(json.dumps(trade) + "\n")
    
    _update_war_chest(trade)
    _update_strategy_stats(trade)

def _update_war_chest(trade: dict):
    try:
        with open(LOG_FILE) as f:
            chest = json.load(f)
    except Exception:
        chest = {
            "total_trades": 0,
            "total_pnl": 0.0,
            "wins": 0,
            "losses": 0,
            "strategies": {},
            "last_updated": None
        }
    
    chest["total_trades"] += 1
    pnl = trade.get("pnl", 0.0)
    chest["total_pnl"] += pnl
    
    if pnl > 0:
        chest["wins"] += 1
    elif pnl < 0:
        chest["losses"] += 1
    
    strategy = trade.get("strategy", "unknown")
    if strategy not in chest["strategies"]:
        chest["strategies"][strategy] = {
            "trades": 0,
            "pnl": 0.0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0
        }
    chest["strategies"][strategy]["trades"] += 1
    chest["strategies"][strategy]["pnl"] += pnl
    if pnl > 0:
        chest["strategies"][strategy]["wins"] += 1
    else:
        chest["strategies"][strategy]["losses"] = chest["strategies"][strategy].get("losses", 0) + 1
    
    s = chest["strategies"][strategy]
    if s["trades"] > 0:
        s["win_rate"] = s["wins"] / s["trades"]
    
    chest["last_updated"] = datetime.utcnow().isoformat()
    
    with open(LOG_FILE, "w") as f:
        json.dump(chest, f, indent=2)

def _update_strategy_stats(trade: dict):
    """Update detailed strategy statistics for AI Intelligence Layer."""
    try:
        with open(STRATEGY_STATS_FILE) as f:
            stats = json.load(f)
    except Exception:
        stats = {}
    
    strategy = trade.get("strategy", "unknown")
    pnl = trade.get("pnl", 0.0)
    
    if strategy not in stats:
        stats[strategy] = {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0.0,
            "consecutive_losses": 0,
            "consecutive_wins": 0,
            "last_trade_time": 0,
            "allocation": 1.0,
            "enabled": True,
            "win_rate": 0.0
        }
    
    stats[strategy]["trades"] += 1
    stats[strategy]["total_pnl"] += pnl
    stats[strategy]["last_trade_time"] = trade.get("timestamp", time.time())
    
    if pnl > 0:
        stats[strategy]["wins"] += 1
        stats[strategy]["consecutive_wins"] += 1
        stats[strategy]["consecutive_losses"] = 0
    else:
        stats[strategy]["losses"] = stats[strategy].get("losses", 0) + 1
        stats[strategy]["consecutive_losses"] += 1
        stats[strategy]["consecutive_wins"] = 0
    
    if stats[strategy]["trades"] > 0:
        stats[strategy]["win_rate"] = stats[strategy]["wins"] / stats[strategy]["trades"]
    
    with open(STRATEGY_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def get_war_chest() -> dict:
    try:
        with open(LOG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def get_strategy_stats(strategy: str = None) -> dict:
    try:
        with open(STRATEGY_STATS_FILE) as f:
            stats = json.load(f)
            if strategy:
                return stats.get(strategy, {})
            return stats
    except Exception:
        return {}

def get_all_trades() -> list:
    trades = []
    if os.path.exists(TRADE_LOG):
        with open(TRADE_LOG) as f:
            for line in f:
                try:
                    trades.append(json.loads(line))
                except Exception:
                    continue
    return trades
