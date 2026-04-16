import requests

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = 7486981713   # your personal chat id (no quotes needed here is fine)

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

r = requests.post(url, json={
    "chat_id": CHAT_ID,
    "text": "🧪 DIRECT TEST FROM LOCAL MACHINE"
})

print(r.text)


