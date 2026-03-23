import os
from flask import Flask
import time
import requests
import json
import threading

app = Flask(__name__)

ULTIMO_LATIDO = time.time()
TIMEOUT = 15
alert_sent = False

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def notify_slack(message):
    print("📩 Enviando a Slack:", message)
    try:
        requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": message},
            timeout=5
        )
    except Exception as e:
        print("❌ Error Slack:", e)

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    global ULTIMO_LATIDO, alert_sent

    ULTIMO_LATIDO = time.time()
    print("💓 Latido recibido")

    if alert_sent:
        notify_slack("🟢 Raspberry volvió a estar ONLINE")
        alert_sent = False

    return {"status": "ok"}

def monitor():
    global alert_sent

    while True:
        tiempo = time.time() - ULTIMO_LATIDO
        print(f"⏱ Tiempo sin latido: {int(tiempo)}s")

        if tiempo > TIMEOUT:
            if not alert_sent:
                print("🚨 SIN SEÑAL")
                notify_slack("🚨 Raspberry OFFLINE o apagada")
                alert_sent = True

        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
