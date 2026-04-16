from flask import Flask
import requests
import os
import time

app = Flask(__name__)

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "-5214518298"
API_KEY = "FVAE7SW1AHUZPC9X"

SYMBOL = "QQQ"  # NASDAQ proxy

state = {
    "range_high": None,
    "range_low": None,
    "breakout": False,
    "ema_outside": False
}

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def get_price_data():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={SYMBOL}&interval=1min&apikey={API_KEY}"
    r = requests.get(url).json()
    return r.get("Time Series (1min)", {})

def calculate_ema(prices, period=14):
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def run_strategy():
    data = get_price_data()
    if not data:
        return

    closes = []
    for time_key in list(data.keys())[:30]:
        closes.append(float(data[time_key]['4. close']))

    if len(closes) < 20:
        return

    current_price = closes[0]
    ema = calculate_ema(closes[:14])

    # Simulated range (first 30 candles)
    state["range_high"] = max(closes)
    state["range_low"] = min(closes)

    # Breakout
    if current_price > state["range_high"]:
        state["breakout"] = True
        send_message("⚡ Breakout detected")

    # EMA outside range
    if ema > state["range_high"] or ema < state["range_low"]:
        state["ema_outside"] = True

    # Retest logic
    if state["breakout"] and state["ema_outside"]:
        if abs(current_price - ema) < 0.1:
            send_message("✅ VALID SETUP: EMA retest")

@app.route('/')
def home():
    return "Engine running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # Run strategy loop
    def loop():
        while True:
            try:
                run_strategy()
                time.sleep(60)
            except:
                time.sleep(60)

    import threading
    threading.Thread(target=loop).start()

    app.run(host='0.0.0.0', port=port)
