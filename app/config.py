"""Configuration of the spam-filter service.

PROMPT_VERSION selects the spam-filter prompt: "v1" or "v2" (see app/spam.py).
You change it in Task 4. It can also be overridden with the PROMPT_VERSION
environment variable when you run the app on your own machine.
"""
import os

PROMPT_VERSION = os.environ.get("PROMPT_VERSION", "v2")

# Set by the Docker build in CI (the git commit). "dev" on your machine.
APP_VERSION = os.environ.get("APP_VERSION", "dev")

# When set, GET /metrics requires the header "Authorization: Bearer <token>".
# Terraform generates the token and gives it to both Render and Grafana Cloud.
METRICS_TOKEN = os.environ.get("METRICS_TOKEN", "")
