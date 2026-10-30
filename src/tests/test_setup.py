
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def read_file(path):
    return (ROOT / path).read_text(encoding="utf-8")


# Issue #1: Python + React project setup

def test_backend_and_frontend_exist():
    assert (ROOT / "backend").is_dir()
    assert (ROOT / "frontend").is_dir()
    assert (ROOT / "tests").is_dir()


def test_required_python_dependencies():
    requirements = read_file("requirements.txt").lower()

    for package in [
        "fastapi",
        "pydantic",
        "pytest",
        "httpx",
        "anthropic",
        "hypothesis",
    ]:
        assert package in requirements


def test_react_project():
    package = json.loads(read_file("frontend/package.json"))
    assert "react" in package.get("dependencies", {})
    assert "dev" in package.get("scripts", {})


def test_required_environment_variables():
    env = read_file(".env.example")

    for key in [
        "ANTHROPIC_API_KEY",
        "LLM_MODEL",
        "SESSION_SECRET",
    ]:
        assert key in env


def test_environment_file_is_gitignored():
    patterns = read_file(".gitignore").splitlines()

    assert any(
        line.strip() in {".env", ".env*"}
        for line in patterns
    )


def test_ci_configuration_exists():
    assert (
        ROOT / ".github" / "workflows" / "ci.yml"
    ).is_file()


def test_ci_runs_pytest():
    ci = read_file(".github/workflows/ci.yml")
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
        ROOT / "docs/prototype/splitwise_ai_demo.html"
    ).is_file()


# Issue #2: User stories and alpha test plan

def test_alpha_testing_scope():
    docs = read_file("docs/alpha-testing.md").lower()

    assert re.search(r"3\s+testers", docs)
    assert re.search(r"6\s+scenarios", docs)
    assert re.search(r"18\s+attempts", docs)
    assert re.search(r"17\s+pass", docs)


def test_hypothesis_is_documented():
    docs = read_file("docs/alpha-testing.md").lower()

    assert "90%" in docs
    assert re.search(r"5\s+prompts", docs)


def test_no_outdated_alpha_targets():
    docs = read_file("docs/alpha-testing.md").lower()

    for outdated in [
        "10 college students",
        "60 attempts",
        "54 passing",
    ]:
        assert outdated not in docs


def test_user_stories_are_documented():
    stories = read_file("docs/UserStories.md")

    for number in range(1, 10):
        assert f"US-{number:02d}" in stories

    assert (
        "Messy Language, Typos, and Unclear Instructions"
        in stories
    )


# Issue #3: Professor's testing-scope decision

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
