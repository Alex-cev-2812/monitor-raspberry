from flask import Flask
import time
import requests
import json
import threading

app = Flask(__name__)

ULTIMO_LATIDO = time.time()
TIMEOUT = 15
alert_sent = False

SLACK_WEBHOOK_URL = "SLACK_WEBHOOK_URL"

def notify_slack(message):
    payload = {"text": message}
    try:
        requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
    except:
        pass

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    global ULTIMO_LATIDO, alert_sent

    ULTIMO_LATIDO = time.time()

    if alert_sent:
        notify_slack("🟢 Raspberry volvió a estar ONLINE")
        alert_sent = False

    return {"status": "ok"}

def monitor():
    global alert_sent

    while True:
        if time.time() - ULTIMO_LATIDO > TIMEOUT:
            if not alert_sent:
                print("🚨 SIN SEÑAL")
                notify_slack("🚨 Raspberry OFFLINE o apagada")
                alert_sent = True

        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)