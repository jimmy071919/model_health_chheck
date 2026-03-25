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

    print(f"Sending LINE broadcast message: {message_text}")
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
            print("Message sent successfully.")
        else:
            print(f"Failed to send message: {response.text}")
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

def report_status():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Reporting bot status...")
    send_alert("機器人運作正常")

import threading
from flask import Flask, request

app = Flask(__name__)

def run_schedule():
    print("Starting model health check bot scheduling...")
    # 啟動時先執行一次測試
    test_url()
    
    # 設定每 1 小時檢查一次 API
    schedule.every(1).hours.do(test_url)
    
    # 設定每 5 小時回報一次狀態
    schedule.every(5).hours.do(report_status)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route("/callback", methods=["POST"])
def callback():
    # 接收來自 LINE 的 webhook 測試或訊息
    print("Received callback request from LINE")
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Model Health Check Bot is running."

def main():
    # 建立一個背景執行緒來跑原本的定時檢查 (這樣才不會擋住 Web 伺服器)
    t = threading.Thread(target=run_schedule, daemon=True)
    t.start()
    
    # 啟動 Flask 伺服器來監聽 Port 5001
    print("Starting Flask web server on port 5001...")
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    main()
