
from pathlib import Path
import json
import re

# Repository structure:
# CS4501_Splitwise/
# ├── src/
# │   ├── backend/
# │   ├── demo/
# │   └── tests/
# ├── docs/
# ├── requirements.txt
# └── pytest.ini

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def read_file(path):
    return (ROOT / path).read_text(encoding="utf-8")


# =========================================================
# Issue #1: Python + React project setup
# =========================================================

def test_backend_and_frontend_exist():
    assert (SRC / "backend").is_dir()
    assert (SRC / "tests").is_dir()
    assert (ROOT / "frontend").is_dir()


def test_required_python_dependencies():
    requirements = read_file("requirements.txt").lower()

    for package in [
        "fastapi",
        "pydantic",
        "pytest",
        "httpx",
        "anthropic",
        "hypothesis",
        "itsdangerous",
    ]:
        assert package in requirements, (
            f"Missing dependency: {package}"
        )


def test_react_project():
    package = json.loads(
        read_file("frontend/package.json")
    )

    assert "react" in package.get("dependencies", {})
    assert "dev" in package.get("scripts", {})


def test_required_environment_variables():
    env = read_file(".env.example")

    for key in [
        "ANTHROPIC_API_KEY",
        "LLM_MODEL",
        "SESSION_SECRET",
    ]:
        assert key in env, (
            f"Missing environment variable: {key}"
        )


def test_environment_file_is_gitignored():
    patterns = read_file(".gitignore").splitlines()

    assert any(
        line.strip() in {".env", ".env*"}
        for line in patterns
    ), ".env must be included in .gitignore"


def test_ci_configuration_exists():
    assert (
        ROOT / ".github" / "workflows" / "ci.yml"
    ).is_file()


def test_ci_runs_pytest():
    ci = read_file(
        ".github/workflows/ci.yml"
    ).lower()

    assert "pytest" in ci


def test_tdd_pull_request_template():
    template = read_file(
        ".github/pull_request_template.md"
    ).lower()

    assert "test" in template
    assert "fail" in template
    assert "review" in template


def test_original_prototype_preserved():
    assert (
        SRC / "demo" / "splitwise_ai_demo.html"
    ).is_file()


# =========================================================
# Issue #2: User stories and Alpha testing plan
# =========================================================

def test_alpha_testing_scope():
    docs = read_file("docs/AlphaTesting.md").lower()

    # Three internal team members
    assert re.search(
        r"(?:testers:\s*3|3\s+(?:development\s+)?team members)",
        docs,
    )

    # Six test scenarios
    assert re.search(
        r"(?:scenarios:\s*6|6\s+scenarios)",
        docs,
    )

    # Eighteen total attempts
    assert re.search(
        r"(?:total test attempts:\s*18|18\s+attempts)",
        docs,
    )

    # At least 17 of 18 attempts must pass
    assert "17 out of 18" in docs or "17/18" in docs


def test_hypothesis_is_documented():
    docs = read_file("docs/AlphaTesting.md").lower()

    assert "90%" in docs
    assert re.search(
        r"5\s+(?:user\s+)?prompts",
        docs,
    )


def test_no_outdated_alpha_targets():
    docs = read_file("docs/AlphaTesting.md").lower()

    for outdated in [
        "10 college students",
        "60 attempts",
        "54 passing",
    ]:
        assert outdated not in docs, (
            f"Outdated Alpha target found: {outdated}"
        )


def test_user_stories_are_documented():
    stories = read_file("docs/UserStories.md")

    # Check that US-01 through US-09 are documented.
    for number in range(1, 10):
        story_id = f"US-{number:02d}"

        assert story_id in stories, (
            f"Missing user story: {story_id}"
        )

    # US-06 should reflect the updated scope.
    assert (
        "Messy Language, Typos, and Unclear Instructions"
        in stories
    )


# =========================================================
# Issue #3: Professor's testing-scope decision
# =========================================================

def test_professor_decision_is_recorded():
    decision = read_file(
        "docs/alpha-validation-decision.md"
    ).lower()

    assert "professor" in decision
    assert "date" in decision

    assert (
        "internal testing" in decision
        or "external testing" in decision
    )


def test_decision_contains_evidence():
    decision = read_file(
        "docs/alpha-validation-decision.md"
    ).lower()

    assert "decision:" in decision
    assert "evidence:" in decision

    # Do not count an unconfirmed decision as completed.
    assert "pending confirmation" not in decision
    assert "awaiting response" not in decision
