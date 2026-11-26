# Lets `pytest` import the `app` package from the repository root, and turns
# off the simulated model latency so the tests run fast.
import os
import sys
from pathlib import Path

os.environ["SIMULATE_LATENCY"] = "0"
os.environ.pop("METRICS_TOKEN", None)
os.environ.pop("PROMPT_VERSION", None)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
