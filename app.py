import requests

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "-5214518298"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

r = requests.post(url, json={
    "chat_id": CHAT_ID,
    "text": "🧪 DIRECT TEST MESSAGE"
})

print(r.text)


