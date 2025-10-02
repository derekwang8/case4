from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line

app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "*"}})

@app.get("/ping")
def ping():
    """Simple health check."""
    return jsonify({"status": "ok", "message": "API is alive", "utc_time": datetime.now(timezone.utc).isoformat()})

@app.get("/time")
def get_time():
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()
    return jsonify({
        "utc_iso": now_utc.isoformat(),
        "local_iso": now_local.isoformat(),
        "server": "flask-warmup"
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

        record = StoredSurveyRecord(
            **submission.dict(),
            received_at=datetime.now(timezone.utc),
            ip=request.headers.get("X-Forwarded-For", request.remote_addr or "")
        )
        append_json_line(record.dict())
        return jsonify({"status": "ok"}), 201

    except ValidationError as ve:
        return jsonify({"error": "validation_error", "detail": ve.errors()}), 422

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
