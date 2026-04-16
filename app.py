from flask import Flask
import requests
import os

app = Flask(__name__)

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "-5214518298"

def send_message():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": "🧪 Bot is LIVE and connected"
    })

@app.route("/")
def home():
    send_message()
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

