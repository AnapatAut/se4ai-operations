"""Telemetry for the spam-filter service (Task 1).

Every metric defined here is exposed by GET /metrics in the Prometheus text
format. Grafana Cloud collects ("scrapes") that page every minute.

One metric is already written for you as an example: BUILD_INFO tells the
dashboard which version of the service and which prompt are running.
"""
from prometheus_client import Counter, Histogram, Info  # noqa: F401

BUILD_INFO = Info("spam_filter_build", "Version of the code and prompt that is running")

# The spam-filter SLO is "99% of checks finish within 0.5 s". To measure it,
# the histogram needs a bucket boundary exactly at 0.5 s.
LATENCY_BUCKETS = (0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)

# TODO Task 1a: a Counter named "spam_requests_total" for every comment checked.
REQUESTS = Counter("spam_requests_total", "Comments checked")

# TODO Task 1b: a Counter named "spam_detected_total" for comments flagged as spam.
SPAM = Counter("spam_detected_total", "Comments flagged as spam")

# TODO Task 1c: a Histogram named "spam_inference_seconds" for the time the
# model takes per comment. Pass buckets=LATENCY_BUCKETS.
LATENCY = Histogram(
    "spam_inference_seconds", "Time the model takes per comment", buckets=LATENCY_BUCKETS
)
