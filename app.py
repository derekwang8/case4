from datetime import datetime, timezone
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/time")
def get_time():
    now_utc = datetime.now(timezone.utc)
    # Local time according to the server’s timezone
    now_local = datetime.now()
    payload = {
        "utc_iso": now_utc.isoformat(),
        "local_iso": now_local.isoformat(),
    }
    return jsonify(payload), 200

@app.get('/ping')
def ping():
    return jsonify({"message": "API is alive"}), 200

@app.get("/time")
def get_time():
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()
    payload = {
        "utc_iso": now_utc.isoformat(),
        "local_iso": now_local.isoformat(),
        "server": "flask-warmup"   # new field
    }
    return jsonify(payload), 200


if __name__ == "__main__":
    # host 0.0.0.0 -> reachable from other devices on your network (optional)
    app.run(host="0.0.0.0", port=0, debug=True)
