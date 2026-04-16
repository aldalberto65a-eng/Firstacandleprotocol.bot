DEBUG = True
def send_debug(price, high, low, ema, state_name):
    if not DEBUG:
        return

    msg = (
        f"📊 DEBUG UPDATE\n"
        f"Price: {price}\n"
        f"Range High: {high}\n"
        f"Range Low: {low}\n"
        f"EMA: {ema}\n"
        f"State: {state_name}"
    )

    send_message(msg)

from flask import Flask
import requests
import os
import time

app = Flask(__name__)

TOKEN = "8767467715:AAH8C8QQ3uCHBJErHaygEaCJxBkIB78ize0"
CHAT_ID = "-1003915488749"
API_KEY = "FVAE7SW1AHUZPC9X"

SYMBOL = "QQQ"

state = {
    "closes": [],
    "range_built": False,
    "range_high": None,
    "range_low": None,
    "breakout": False,
    "ema_ok": False
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
    for p in prices[-period+1:]:
        ema = p * k + ema * (1 - k)
    return ema

def run_engine():
    data = get_data()
    if not data:
        return
        if not state["range_built"]:
    state_name = "BUILDING RANGE"
elif not state["breakout"]:
    state_name = "WAITING BREAKOUT"
elif not state["ema_ok"]:
    state_name = "WAITING EMA CONFIRMATION"
else:
    state_name = "WAITING RETEST"
send_debug(
    price,
    state["range_high"],
    state["range_low"],
    ema if 'ema' in locals() else None,
    state_name
)


    closes = [float(v["4. close"]) for v in data.values()]
    if len(closes) < 40:
        return

    price = closes[0]

    # STEP 1 — Build range (first 30 candles)
    if not state["range_built"]:
        state["range_high"] = max(closes[:30])
        state["range_low"] = min(closes[:30])
        state["range_built"] = True

        send_message(
            f"📦 Range locked\nHigh: {state['range_high']}\nLow: {state['range_low']}"
        )
        return

    # STEP 2 — Breakout confirmation (CLOSE logic approximation)
    if not state["breakout"]:
        if price > state["range_high"]:
            state["breakout"] = True
            send_message("⚡ Breakout ABOVE range")
        elif price < state["range_low"]:
            state["breakout"] = True
            send_message("⚡ Breakout BELOW range")
        return

    # STEP 3 — EMA filter
    ema = calculate_ema(closes)

    if ema:
        if ema > state["range_high"] or ema < state["range_low"]:
            state["ema_ok"] = True

    # STEP 4 — Retest trigger
    if state["breakout"] and state["ema_ok"] and ema:
        if abs(price - ema) < 0.2:
            send_message("✅ VALID FIRST CANDLE SETUP (EMA RETEST)")
            state["breakout"] = False
            state["ema_ok"] = False

@app.route("/")
def home():
    return "First Candle Engine Running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    def loop():
        while True:
            try:
                run_engine()
                time.sleep(60)
            except Exception as e:
                print("ERROR:", e)
                time.sleep(60)

    import threading
    threading.Thread(target=loop).start()
    app.run(host="0.0.0.0", port=port)


