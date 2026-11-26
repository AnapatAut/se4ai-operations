"""A tiny stand-in for the lecture's LLM spam filter.

The real service runs a 50B-parameter LLM on a GPU. This one scores a comment
with a few keyword rules, then sleeps for a moment to behave like a slow model.
That is enough to produce realistic telemetry: some comments are spam, and
every check takes some time.

Each "prompt version" is a different configuration of the model:

* v1: the current prompt. Fast, and only flags clear spam.
* v2: a longer prompt with many more examples. It is slower, and it is so
  strict that it also flags real comments that contain a link.

You do not need to edit this file.
"""
import os
import random
import re
import time

SPAM_WORDS = {
    "free": 0.20,
    "winner": 0.35,
    "prize": 0.30,
    "crypto": 0.30,
    "bitcoin": 0.30,
    "casino": 0.40,
    "loan": 0.25,
    "cheap": 0.20,
    "click": 0.20,
    "offer": 0.15,
    "guaranteed": 0.25,
}

PROMPTS = {
    # threshold: score at or above which a comment is spam
    # latency_ms: (mean, standard deviation) of the simulated inference time
    "v1": {"threshold": 0.50, "latency_ms": (60, 20)},
    "v2": {"threshold": 0.20, "latency_ms": (450, 150)},
}

_LINK = re.compile(r"https?://|www\.", re.IGNORECASE)
_WORD = re.compile(r"[a-z]+")


def score(text):
    """Return a spam score between 0.0 and 1.0."""
    words = _WORD.findall(text.lower())
    total = sum(SPAM_WORDS.get(word, 0.0) for word in words)
    total += 0.25 * min(len(_LINK.findall(text)), 2)
    letters = [c for c in text if c.isalpha()]
    if len(letters) >= 10 and sum(c.isupper() for c in letters) / len(letters) > 0.5:
        total += 0.20  # SHOUTING
    if "!!!" in text:
        total += 0.10
    return round(min(total, 1.0), 3)


def _simulate_inference(prompt_version):
    """Sleep like a slow model would. Disabled when SIMULATE_LATENCY=0 (tests)."""
    if os.environ.get("SIMULATE_LATENCY", "1") == "0":
        return
    mean, sd = PROMPTS[prompt_version]["latency_ms"]
    ms = max(5.0, random.gauss(mean, sd))
    if random.random() < 0.01:  # the occasional very slow request
        ms *= 4
    time.sleep(ms / 1000)


def check(text, prompt_version):
    """Check one comment. Returns (is_spam, score)."""
    if prompt_version not in PROMPTS:
        raise ValueError(f"unknown prompt version {prompt_version!r}")
    _simulate_inference(prompt_version)
    s = score(text)
    return s >= PROMPTS[prompt_version]["threshold"], s
