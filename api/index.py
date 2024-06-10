
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, jsonify
import requests
from datetime import datetime
app = Flask(__name__)


def claim(init_data):
    headers = {
        "Accept": "*/*",
        "Referer": "https://0xiceberg.store/webapp/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "X-Telegram-Auth": init_data,
    }
    response = requests.get("https://0xiceberg.store/api/v1/web-app/farming/", headers=headers)
    if response.status_code != 200:
        return False, response.json()['detail']
    if response.headers.get("date") is None:
        return False, "Date Tidak Terdeteksi"
    if response.text == "":
        start_farm_response = requests.post("https://0xiceberg.store/api/v1/web-app/farming/", headers=headers)
        if start_farm_response.status_code != 200:
            return False, start_farm_response.json()['detail']
        return True, start_farm_response.json()
    stop_date = datetime.strptime(response.json()['stop_time'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    date_now = datetime.strptime(response.headers.get("date"), "%a, %d %b %Y %H:%M:%S %Z").timestamp()
    if int(date_now) >= int(stop_date):
        collect_response = requests.delete("https://0xiceberg.store/api/v1/web-app/farming/collect/", headers=headers)
        if collect_response.status_code != 200:
            return False, collect_response.json()['detail']
        start_farm_response = requests.post("https://0xiceberg.store/api/v1/web-app/farming/", headers=headers)
        if start_farm_response.status_code != 200:
            return False, start_farm_response.json()['detail']
        return True, collect_response.json()
    seconds = int(stop_date) - int(date_now)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return False, f"Masih menunggu {hours}:{minutes:02}:{seconds:02} Detik Lagi"

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/iceberg')
def iceberg_claim():
    if request.headers.get('Init-Data') is None:
        return jsonify({"status": False, "message": "headers Init-Data not found"}), 400
    try:
        status_response, response = claim(init_data=request.headers.get("Init-Data"))
        if not status_response:
            return jsonify({"status": False, "message": response}), 400

        return jsonify({"status": True, "data": response}), 200
    except Exception as e:
        return jsonify({"status": False, "message": str(e)}), 400

