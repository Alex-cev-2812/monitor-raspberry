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

    ahora = time.time()

    # 🟢 PRIMERA VEZ (INICIADA)
    if device not in DISPOSITIVOS:
        notify_slack(f"🟢 {device} INICIADA")

        DISPOSITIVOS[device] = {
            "last_seen": ahora,
            "estado": "online"
        }
        return {"status": "ok"}

    # 🟢 VOLVIÓ DESPUÉS DE ESTAR OFFLINE
    if DISPOSITIVOS[device]["estado"] == "offline":
        notify_slack(f"🟢 {device} ONLINE")

        DISPOSITIVOS[device]["estado"] = "online"

    # Actualizar tiempo
    DISPOSITIVOS[device]["last_seen"] = ahora

    print(f"💓 {device} activo")
    return {"status": "ok"}

def monitor():
    while True:
        ahora = time.time()

        for device, info in DISPOSITIVOS.items():
            tiempo = ahora - info["last_seen"]

            # 🚨 OFFLINE
            if tiempo > TIMEOUT and info["estado"] == "online":
                notify_slack(f"🚨 {device} OFFLINE")
                DISPOSITIVOS[device]["estado"] = "offline"

        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
