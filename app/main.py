"""The spam-filter web service.

    GET  /         a page with a comment box, to try the filter by hand
    POST /check    {"text": "..."}  ->  {"spam": true, "score": 0.85, "prompt_version": "v1"}
    GET  /health   used by Render to know that the service is up
    GET  /metrics  telemetry in the Prometheus text format

Run it on your machine with:  flask --app app.main run --port 8080
"""
import hmac

from flask import Flask, Response, jsonify, render_template, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app import metrics, spam
from app.config import APP_VERSION, METRICS_TOKEN, PROMPT_VERSION

app = Flask(__name__)
metrics.BUILD_INFO.info({"version": APP_VERSION, "prompt_version": PROMPT_VERSION})


@app.get("/")
def index():
    return render_template("index.html", prompt_version=PROMPT_VERSION, version=APP_VERSION)


@app.post("/check")
def check():
    body = request.get_json(silent=True) or {}
    text = body.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify(error='send JSON like {"text": "your comment"}'), 400

    # TODO Task 1d: count this request with metrics.REQUESTS,
    # and time the model call below with metrics.LATENCY.
    metrics.REQUESTS.inc()
    with metrics.LATENCY.time():
        is_spam, score = spam.check(text, PROMPT_VERSION)

    # TODO Task 1e: if the comment is spam, count it with metrics.SPAM.
    if is_spam:
        metrics.SPAM.inc()

    return jsonify(spam=is_spam, score=score, prompt_version=PROMPT_VERSION)


@app.get("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION, prompt_version=PROMPT_VERSION)


@app.get("/metrics")
def prometheus_metrics():
    # The public URL is on the internet, so only Grafana Cloud (which knows the
    # token) may read the telemetry. Without a token (on your machine) it is open.
    if METRICS_TOKEN:
        expected = f"Bearer {METRICS_TOKEN}"
        if not hmac.compare_digest(request.headers.get("Authorization", ""), expected):
            return Response("unauthorized\n", status=401)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
