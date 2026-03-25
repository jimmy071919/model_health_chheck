import os
import time
import requests
import schedule
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("Channel_access_token")
CHANNEL_SECRET = os.getenv("Channel_secret")
MODEL_TOKEN = os.getenv("model_token")

URL = "https://oneapi.dev-serve.me/v1/chat/completions"
MODEL = "GPT-5"

def send_alert(message_text):
    if not CHANNEL_ACCESS_TOKEN:
        print("Error: Channel_access_token not found in .env")
        return

    print("API is down or failed, sending LINE broadcast message...")
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print("Alert sent successfully.")
        else:
            print(f"Failed to send alert: {response.text}")
    except Exception as e:
        print(f"Error sending LINE message: {str(e)}")

def test_url():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking API status...")
    if not MODEL_TOKEN:
        print("Error: model_token not found in .env")
        return

    headers = {
        "Authorization": f"Bearer {MODEL_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "health check"}
        ],
        "max_tokens": 5
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            print("API test passed, no message sent.")
        else:
            alert_msg = f"Model API Failed.\nStatus Code: {response.status_code}\nModel: {MODEL}"
            send_alert(alert_msg)
    except requests.exceptions.RequestException:
        alert_msg = f"Model API Request Error.\nError: Connection failed or timeout.\nURL: {URL}"
        send_alert(alert_msg)

def main():
    print("Starting model health check bot...")
    # 啟動時先執行一次測試
    test_url()
    
    # 設定每 1 小時執行一次
    schedule.every(1).hours.do(test_url)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
