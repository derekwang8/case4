from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line

app = Flask(__name__)
# Allow cross-origin requests so the static HTML can POST from localhost or file://
CORS(app, resources={r"/v1/*": {"origins": "*"}})

@app.route("/ping", methods=["GET"])
def ping():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "API is alive",
        "utc_time": datetime.now(timezone.utc).isoformat()
    })

@app.post("/v1/survey")
def submit_survey():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json", "detail": "Body must be application/json"}), 400

    try:
        submission = SurveySubmission(**payload)

        if not submission.user_agent:
            submission.user_agent = request.headers.get("User-Agent")

        record = submission.to_safe_dict()

        record["received_at"] = datetime.now(timezone.utc).isoformat()
        record["ip"] = request.remote_addr
        record["user_agent"] = submission.user_agent

    except ValidationError as ve:
        return jsonify({"error": "validation_error", "detail": ve.errors()}), 422

    record = StoredSurveyRecord(
        **submission.dict(),
        received_at=datetime.now(timezone.utc),
        ip=request.headers.get("X-Forwarded-For", request.remote_addr or "")
    )
    append_json_line(record.dict())
    return jsonify({"status": "ok"}), 201

if __name__ == "__main__":
    app.run(port=0, debug=True)

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
