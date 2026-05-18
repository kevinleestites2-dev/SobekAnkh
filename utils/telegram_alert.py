"""
Sobek Ankh — Telegram Alert System
Inherits ZeusPrime's Telegram config. Sobek speaks through the same channel.

v2.0 — Enhanced notifications:
- Trade closed alerts with full details
- Strategy performance alerts
- AI Intelligence Layer alerts
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8679655550:AAGUB1m5fmqHc8OHqqM24Vixz8FfwX-gqD4")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7135054241")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_alert(message: str, silent: bool = False) -> bool:
    """Send alert to Forgemaster via Telegram."""
    try:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_notification": silent
        }
        r = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM] Alert failed: {e}")
        return False

def send_trade_closed(trade: dict, cumulative_pnl: float = 0.0) -> bool:
    """Send notification for every closed trade with full details."""
    strategy = trade.get("strategy", "unknown")
    entry = trade.get("entry", 0.0)
    exit_price = trade.get("exit", 0.0)
    pnl = trade.get("pnl", 0.0)
    outcome = trade.get("outcome", "WIN" if pnl > 0 else "LOSS")
    timestamp = trade.get("timestamp", 0)
    
    if isinstance(timestamp, (int, float)):
        ts = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    else:
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    emoji = "🟢" if pnl > 0 else "🔴"
    
    message = (
        f"📊 <b>Trade Closed</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ Strategy: {strategy}\n"
        f"💵 Entry: ${entry:.4f}\n"
        f"💰 Exit: ${exit_price:.4f}\n"
        f"📈 PnL: {pnl:+.4f} USDT\n"
        f"✅ Result: {emoji} {outcome}\n"
        f"⏰ {ts}\n"
        f"💰 Total: {cumulative_pnl:+.4f} USDT"
    )
    
    return send_alert(message)

def send_critical(message: str) -> bool:
    return send_alert(f"🚨 CRITICAL\n{message}", silent=False)

def send_profit_report(daily_pnl: float, total_trades: int, win_rate: float, capital: float):
    msg = (
        f"🐊 SOBEK DAILY REPORT\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💰 Daily PnL: {'+'if daily_pnl>=0 else ''}{daily_pnl:.2f} USDT\n"
        f"📊 Trades: {total_trades}\n"
        f"🎯 Win Rate: {win_rate:.1%}\n"
        f"🏦 Capital: ${capital:.2f}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"For the War Chest. For the Pantheon. 🔱"
    )
    return send_alert(msg)

def send_ai_analysis(killed: list, promoted: list, demoted: list, regime: str):
    msg = f"🧠 <b>AI Strategy Analysis</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if killed:
        msg += f"🔴 KILLED: {', '.join(killed)}\n"
    if promoted:
        msg += f"🟢 PROMOTED: {', '.join(promoted)}\n"
    if demoted:
        msg += f"🟡 DEMOTED: {', '.join(demoted)}\n"
    
    if not killed and not promoted and not demoted:
        msg += "📊 No changes - all strategies performing within thresholds\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🌊 Active regime: {regime}\n"
    
    return send_alert(msg)

def send_backtest_report(results: dict):
    msg = f"📊 <b>Backtest Report (30 days)</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]["total_pnl"], reverse=True)
    
    for strat, metrics in sorted_results:
        msg += f"\n<b>{strat}</b>\n"
        msg += f"  Trades: {metrics['total_trades']} | Win: {metrics['win_rate']:.1%}\n"
        msg += f"  PnL: {metrics['total_pnl']:+.4f} USDT\n"
        msg += f"  Max DD: {metrics['max_drawdown']:.2%} | Sharpe: {metrics['sharpe_ratio']:.2f}\n"
    
    return send_alert(msg)
