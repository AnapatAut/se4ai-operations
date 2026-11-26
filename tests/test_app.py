"""Tests of the service itself. These pass from the start."""
import pytest

from app import main, spam

HAM = "Great post, thanks for the clear explanation of SLOs!"
SPAM = "WINNER!!! Claim your FREE crypto prize now: http://example.com"
HAM_WITH_LINK = "Nice article. I wrote a follow-up here: https://example.org/blog"


def test_index_page(client):
    assert client.get("/").status_code == 200


def test_health(client):
    assert client.get("/health").get_json()["status"] == "ok"


def test_ham_is_published(client):
    data = client.post("/check", json={"text": HAM}).get_json()
    assert data["spam"] is False


def test_spam_is_blocked(client):
    data = client.post("/check", json={"text": SPAM}).get_json()
    assert data["spam"] is True
    assert 0.5 <= data["score"] <= 1.0


def test_empty_comment_is_rejected(client):
    assert client.post("/check", json={"text": "   "}).status_code == 400
    assert client.post("/check", data="not json").status_code == 400


def test_v2_also_flags_real_comments_with_links():
    assert spam.check(HAM_WITH_LINK, "v1")[0] is False
    assert spam.check(HAM_WITH_LINK, "v2")[0] is True


def test_metrics_page_is_open_without_token(client):
    assert client.get("/metrics").status_code == 200


@pytest.mark.parametrize("header, status", [
    (None, 401),
    ("Bearer wrong", 401),
    ("Bearer s3cret", 200),
])
def test_metrics_page_needs_token_when_set(client, monkeypatch, header, status):
    monkeypatch.setattr(main, "METRICS_TOKEN", "s3cret")
    headers = {"Authorization": header} if header else {}
    assert client.get("/metrics", headers=headers).status_code == status
