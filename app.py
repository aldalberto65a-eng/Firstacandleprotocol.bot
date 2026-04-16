from flask import Flask
import requests
import os
import time
from datetime import datetime

app = Flask(__name__)

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "-5214518298"
API_KEY = "FVAE7SW1AHUZPC9X"

SYMBOL = "QQQ"

state = {
    "range_built": False,
    "range_high": None,
    "range_low": None,
    "breakout": False,
    "ema_outside": False
}

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def get_data():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={SYMBOL}&interval=1min&apikey={API_KEY}"
    r = requests.get(url).json()
    return r.get("Time Series (1min)", {})

def calculate_ema(prices, period=14):
    if len(prices) < period:
        return None
    k = 2 / (period + 1)
    ema = prices[-period]
    for price in prices[-period+1:]:
        ema = price * k + ema * (1 - k)
    return ema

send_message("🧪 Engine is alive")

def run_engine():
    data = get_data()
    if not data:
        return

    closes = [float(v["4. close"]) for v in data.values()]

    if len(closes) < 20:
        return

    price = closes[0]

    # STEP 1 — Build range once
    if not state["range_built"]:
        state["range_high"] = max(closes[:30])
        state["range_low"] = min(closes[:30])
        state["range_built"] = True
        send_message(f"📦 Range locked:\nHigh: {state['range_high']}\nLow: {state['range_low']}")
        return

    # STEP 2 — Breakout confirmation (CLOSE only logic approximation)
    if not state["breakout"]:
        if price > state["range_high"]:
            state["breakout"] = True
            send_message("⚡ Breakout confirmed (above range)")
        elif price < state["range_low"]:
            state["breakout"] = True
            send_message("⚡ Breakout confirmed (below range)")
        return

    # STEP 3 — EMA filter
    ema = calculate_ema(closes)
    if ema:
        if ema > state["range_high"] or ema < state["range_low"]:
            state["ema_outside"] = True

    # STEP 4 — Retest logic
    if state["breakout"] and state["ema_outside"] and ema:
        if abs(price - ema) < 0.2:
            send_message("✅ VALID SETUP: EMA retest confirmed (First Candle Protocol)")
            state["breakout"] = False  # reset after signal

@app.route('/')
def home():
    return "Engine V2 running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    import threading
    def loop():
        while True:
            try:
                run_engine()
                time.sleep(60)
            except:
                time.sleep(60)

    threading.Thread(target=loop).start()
    app.run(host="0.0.0.0", port=port)

