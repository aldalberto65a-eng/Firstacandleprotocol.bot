from flask import Flask
import requests
import os
import time
import threading

app = Flask(__name__)

TOKEN = "8767467715:AAH8C8QQ3uCHBJErHaygEaCJxBkIB78ize0"
CHAT_ID = "-1003915488749"
API_KEY = "FVAE7SW1AHUZPC9X"

SYMBOL = "QQQ"
DEBUG = True

state = {
    "range_built": False,
    "range_high": None,
    "range_low": None,
    "breakout": False,
    "ema_ok": False
}

# ---------------- TELEGRAM ---------------- #

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# ---------------- DATA ---------------- #

def get_data():
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={SYMBOL}&interval=1min&apikey={API_KEY}"
        r = requests.get(url, timeout=10).json()
        return r.get("Time Series (1min)", {})
    except Exception as e:
        print("Data error:", e)
        return {}

def calculate_ema(prices, period=14):
    if len(prices) < period:
        return None

    k = 2 / (period + 1)
    ema = prices[-period]

    for p in prices[-period + 1:]:
        ema = (p * k) + (ema * (1 - k))

    return ema

# ---------------- ENGINE ---------------- #

def run_engine():
    data = get_data()
    if not data:
        return

    sorted_data = sorted(data.items(), reverse=True)
    closes = [float(v[1]["4. close"]) for v in sorted_data]

    if len(closes) < 40:
        return

    price = closes[0]
    ema_value = calculate_ema(closes)

    # ---------------- RANGE ---------------- #

    if not state["range_built"]:
        session = closes[:30]
        state["range_high"] = max(session)
        state["range_low"] = min(session)
        state["range_built"] = True

        send_message(
            f"📦 RANGE LOCKED\nHigh: {state['range_high']}\nLow: {state['range_low']}"
        )
        return

    # ---------------- BREAKOUT ---------------- #

    if not state["breakout"]:
        if price > state["range_high"] * 1.0005:
            state["breakout"] = True
            send_message("⚡ BREAKOUT ABOVE RANGE")

        elif price < state["range_low"] * 0.9995:
            state["breakout"] = True
            send_message("⚡ BREAKOUT BELOW RANGE")

        return

    # ---------------- EMA FILTER ---------------- #

    if ema_value:
        if ema_value > state["range_high"] or ema_value < state["range_low"]:
            state["ema_ok"] = True

    # ---------------- STATE ---------------- #

    if not state["range_built"]:
        state_name = "BUILDING RANGE"
    elif not state["breakout"]:
        state_name = "WAITING BREAKOUT"
    elif not state["ema_ok"]:
        state_name = "WAITING EMA CONFIRMATION"
    else:
        state_name = "WAITING RETEST"

    # ---------------- DEBUG ---------------- #

    if DEBUG:
        send_message(
            f"📊 DEBUG\n"
            f"Price: {price}\n"
            f"Range: {state['range_low']} - {state['range_high']}\n"
            f"EMA: {ema_value}\n"
            f"State: {state_name}"
        )

# ---------------- FLASK ---------------- #

@app.route("/")
def home():
    return "First Candle Engine Running"

# ---------------- LOOP ---------------- #

def loop():
    while True:
        try:
            run_engine()
            time.sleep(60)
        except Exception as e:
            print("Loop error:", e)
            time.sleep(60)

if __name__ == "__main__":
    thread = threading.Thread(target=loop)
    thread.daemon = True
    thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


