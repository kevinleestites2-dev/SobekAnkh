#!/usr/bin/env python3
"""
reset_memory.py — Wipe poisoned SAFLA memory.
Removes all zero-pnl ghost trades. Keeps any real trades (pnl != 0).
Run once after updating to v2.1, then restart sobek_ankh.py.
"""
import json
from pathlib import Path

MEMORY_DIR = Path("memory")
TRADE_LOG  = MEMORY_DIR / "trade_log.json"
PERF_FILE  = MEMORY_DIR / "strategy_performance.json"

def reset():
    if TRADE_LOG.exists():
        trades = json.loads(TRADE_LOG.read_text())
        before = len(trades)
        real   = [t for t in trades if float(t.get("pnl", 0)) != 0]
        TRADE_LOG.write_text(json.dumps(real, indent=2))
        print(f"Trade log: {before} → {len(real)} trades ({before - len(real)} ghost trades removed)")
    else:
        print("No trade log found.")

    if PERF_FILE.exists():
        PERF_FILE.write_text(json.dumps({
            "updated_at": "reset",
            "regime": "NEUTRAL",
            "performance": {}
        }, indent=2))
        print("strategy_performance.json reset.")

    print("
✅ Memory clean. Restart sobek_ankh.py now.")

if __name__ == "__main__":
    reset()
