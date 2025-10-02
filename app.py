import hashlib
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line

app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "*"}})

@app.route("/ping", methods=["GET"])
def ping():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "API is alive",
        "utc_time": datetime.now(timezone.utc).isoformat()
    })

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
    try:
        payload = request.get_json(silent=True)
        print("DEBUG payload:", payload)
        if payload is None:
            return jsonify({"error": "invalid_json", "detail": "Body must be application/json"}), 400
    
        submission = SurveySubmission(**payload)

        email_hash = hashlib.sha256(submission.email.encode()).hexdigest()
        age_hash = hashlib.sha256(str(submission.age).encode()).hexdigest()

        if submission.submission_id:
            submission_id = submission.submission_id
        else:
            now_str = datetime.now(timezone.utc).strftime("%Y%m%d%H")
            submission_id = hashlib.sha256((submission.email + now_str).encode()).hexdigest()

        record = StoredSurveyRecord(
            name=submission.name,
            email_hash=email_hash,
            age_hash=age_hash,
            consent=submission.consent,
            rating=submission.rating,
            comments=submission.comments,
            user_agent=submission.user_agent,
            submission_id=submission_id,
            received_at=datetime.now(timezone.utc),
            ip=request.headers.get("X-Forwarded-For", request.remote_addr or "")
        )
        append_json_line(record.dict())
        return jsonify({"status": "ok"}), 201

    except ValidationError as ve:
        return jsonify({"error": "validation_error", "detail": ve.errors()}), 422
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": "request_failed", "detail": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
