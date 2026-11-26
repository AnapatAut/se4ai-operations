"""Task 2: the CI/CD workflow must deploy only tested images, only from main."""
from pathlib import Path

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci-cd.yml"


@pytest.fixture
def deploy():
    jobs = yaml.safe_load(WORKFLOW.read_text())["jobs"]
    return jobs.get("deploy") or {}


def test_deploy_job_exists(deploy):
    assert deploy, "There is no deploy job yet: uncomment it in ci-cd.yml"


def test_no_placeholders_left():
    lines = [line for line in WORKFLOW.read_text().splitlines() if not line.lstrip().startswith("#")]
    assert not any("???" in line for line in lines), "Replace every ??? in ci-cd.yml"


def test_deploy_runs_after_build(deploy):
    needs = deploy.get("needs")
    needs = [needs] if isinstance(needs, str) else (needs or [])
    assert "build" in needs, "deploy must wait for the build job (it also needs its output)"


def test_deploy_only_from_main_and_when_configured(deploy):
    condition = str(deploy.get("if", ""))
    assert "refs/heads/main" in condition, "deploy only from the main branch"
    assert "vars.RENDER_SERVICE_ID" in condition, "skip the deploy until RENDER_SERVICE_ID is set"


def test_deploy_uses_the_api_key_secret(deploy):
    steps = [s for s in deploy.get("steps", []) if "render_deploy.sh" in s.get("run", "")]
    assert steps, "the deploy job must run tools/render_deploy.sh"
    key = str(steps[0].get("env", {}).get("RENDER_API_KEY", "")).replace(" ", "")
    assert key == "${{secrets.RENDER_API_KEY}}", (
        "read the API key from the secret, never write the key itself in the file"
    )
