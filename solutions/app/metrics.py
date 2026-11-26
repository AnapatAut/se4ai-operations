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

# Task 1a
REQUESTS = Counter("spam_requests_total", "Comments checked")

# Task 1b
SPAM = Counter("spam_detected_total", "Comments flagged as spam")

# Task 1c
LATENCY = Histogram("spam_inference_seconds", "Spam-filter inference latency", buckets=LATENCY_BUCKETS)
