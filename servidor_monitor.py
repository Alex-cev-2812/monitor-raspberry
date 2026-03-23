import os
from flask import Flask, request
import time
import requests
import threading

app = Flask(__name__)

DISPOSITIVOS = {}
TIMEOUT = 15

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def notify_slack(message):
    print("📩", message)
    try:
        requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": message},
            timeout=5
        )
    except:
        pass

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    device = data.get("device", "unknown")

    DISPOSITIVOS[device] = {
        "last_seen": time.time(),
        "alert_sent": False
    }

    print(f"💓 {device} activo")

    return {"status": "ok"}

def monitor():
    while True:
        ahora = time.time()

        for device, info in DISPOSITIVOS.items():
            tiempo = ahora - info["last_seen"]

            if tiempo > TIMEOUT and not info["alert_sent"]:
                notify_slack(f"🚨 {device} OFFLINE")
                DISPOSITIVOS[device]["alert_sent"] = True

            elif tiempo <= TIMEOUT and info["alert_sent"]:
                notify_slack(f"🟢 {device} ONLINE")
                DISPOSITIVOS[device]["alert_sent"] = False

        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
