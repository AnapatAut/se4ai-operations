"""Task 1: the service must expose the three metrics of the spam-filter SLOs."""
from prometheus_client import REGISTRY

HAM = "Great post, thanks for the clear explanation of SLOs!"
SPAM = "WINNER!!! Claim your FREE crypto prize now: http://example.com"


def value(name, labels=None):
    """Current value of one metric sample, or 0 if it does not exist yet."""
    return REGISTRY.get_sample_value(name, labels or {}) or 0.0


def test_metrics_are_exposed(client):
    page = client.get("/metrics").get_data(as_text=True)
    for line in (
        "# TYPE spam_requests_total counter",
        "# TYPE spam_detected_total counter",
        "# TYPE spam_inference_seconds histogram",
    ):
        assert line in page, f"/metrics does not contain: {line}"


def test_every_check_is_counted(client):
    before = value("spam_requests_total")
    client.post("/check", json={"text": HAM})
    client.post("/check", json={"text": SPAM})
    assert value("spam_requests_total") - before == 2


def test_only_spam_is_counted_as_spam(client):
    before = value("spam_detected_total")
    client.post("/check", json={"text": HAM})
    assert value("spam_detected_total") - before == 0
    client.post("/check", json={"text": SPAM})
    assert value("spam_detected_total") - before == 1


def test_bad_requests_are_not_counted(client):
    before = value("spam_requests_total")
    client.post("/check", json={"text": ""})
    assert value("spam_requests_total") - before == 0


def test_every_check_is_timed(client):
    before = value("spam_inference_seconds_count")
    client.post("/check", json={"text": HAM})
    assert value("spam_inference_seconds_count") - before == 1


def test_latency_histogram_has_a_bucket_at_the_slo(client):
    # The SLO is "99% of checks within 0.5 s": we need the bucket le="0.5".
    client.post("/check", json={"text": HAM})
    assert REGISTRY.get_sample_value("spam_inference_seconds_bucket", {"le": "0.5"}) is not None
