
# Splitwise AI — Developer Setup Guide

This guide explains how to set up and run the Splitwise AI application locally.

## 1. Tech Stack

### Frontend
- React
- JavaScript
- Vite
- npm

### Backend
- Python 3.13
- FastAPI
- Pydantic
- SQLite
- Anthropic Claude API

### Testing
- pytest
- Hypothesis
- FastAPI TestClient

---

## 2. Prerequisites

Install the following before starting:

- Git
- Python 3.13
- Node.js and npm
- Visual Studio Code (recommended)

Verify the installations:

```bash
git --version
py --version
node -v
npm -v
```

**Note for macOS/Linux:** Use `python3` instead of `py` if the Python launcher is unavailable.

---

## 3. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/wangrui04/CS4501_Splitwise.git
cd CS4501_Splitwise
```

To work on the existing Alpha backend branch:

```bash
git fetch origin
git switch feature/alpha-backend-core
```

If the branch has not been merged yet, make sure you switch to it before running the setup instructions.

---

## 4. Backend Setup

### Create a Python Virtual Environment

From the repository root:

```bash
py -m venv .venv
```

Activate it on Windows Git Bash:

```bash
source .venv/Scripts/activate
```

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

For macOS/Linux:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
py -m pip install -r requirements.txt
```

For macOS/Linux, use:

```bash
python3 -m pip install -r requirements.txt
```

---

## 5. Environment Variables

The repository contains a `.env.example` file listing the configuration variables needed by the application.

Create a local `.env` file by copying it:

```bash
cp .env.example .env
```

The file should contain:

```dotenv
ANTHROPIC_API_KEY=
LLM_MODEL=
SESSION_SECRET=
```

### Environment Variable Descriptions

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | API key for Claude |
| `LLM_MODEL` | Anthropic Claude model identifier |
| `SESSION_SECRET` | Random secret used to sign user sessions |

Ask a teammate responsible for API configuration for the appropriate development settings.

**Important:**
- Never commit `.env` to GitHub.
- Never share API keys through GitHub issues or pull requests.
- Keep `.env.example` free of real secrets.

The automated tests use mock AI responses, so an Anthropic API key is not required to run the test suite.

---

## 6. Frontend Setup

From the repository root:

```bash
cd frontend
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Open the URL displayed in the terminal, typically:

http://localhost:5173/

Keep this terminal running while using the frontend.

---

## 7. Backend Server

The backend currently exposes its FastAPI application through a `create_app()` factory that requires a database connection and session secret.

Before starting a standalone API server, a development entry point must initialize the database and call `create_app()`.

Once that entry point is configured, FastAPI can be started through Uvicorn.

**Note:** At this stage, the frontend and backend are separate. Frontend-to-backend integration is still a development task.

---

## 8. Running Automated Tests

Make sure Python dependencies are installed.

From the repository root, run:

```bash
py -m pytest src/tests/ -v
```

To run individual test files:

### Setup Tests

```bash
py -m pytest src/tests/test_setup.py -v
```

### Expense Calculation Tests

```bash
py -m pytest src/tests/test_expense.py -v
```

### Expense Validation Tests

```bash
py -m pytest src/tests/test_validator.py -v
```

### Database and Backend API Tests

```bash
py -m pytest src/tests/test_backend.py -v
```

### LLM and Conversation Pipeline Tests

```bash
py -m pytest src/tests/test_llm.py -v
```

### Expected Result

At the time this setup guide was prepared, all 121 tests passed in the development environment.

Run the suite locally to confirm that your installation is working.

---

## 9. Project Structure

```text
CS4501_Splitwise/
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   └── pull_request_template.md
├── docs/
│   ├── AlphaTesting.md
│   ├── UserStories.md
│   └── alpha-validation-decision.md
├── frontend/
│   ├── package.json
│   └── src/
├── src/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── allocation.py
│   │   ├── database.py
│   │   ├── llm.py
│   │   ├── main.py
│   │   ├── pipeline.py
│   │   ├── repository.py
│   │   ├── schemas.py
│   │   └── validator.py
│   ├── demo/
│   └── tests/
│       ├── test_setup.py
│       ├── test_expense.py
│       ├── test_validator.py
│       ├── test_backend.py
│       └── test_llm.py
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
├── README.md
└── SETUP.md
```

---

## 10. Git Workflow

Always check which branch you are on:

```bash
git branch
```

Before starting new work:

```bash
git pull
```

For a new feature, create a separate branch:

```bash
git switch -c feature/your-feature-name
```

After making changes:

```bash
git status
git add .
git commit -m "feat: describe your change"
git push -u origin feature/your-feature-name
```

Open a pull request on GitHub and reference the relevant issue.

### Before Opening a Pull Request

- Run the relevant tests.
- Check that no secrets or `.env` files are tracked.
- Confirm that changes satisfy the GitHub issue acceptance criteria.
- Review AI-generated code and tests.
- Complete the pull request template.

---

## 11. Troubleshooting

### `npm: command not found`

Install Node.js and restart VS Code or the terminal.

### `No module named backend`

Run pytest from the repository root and ensure `pytest.ini` contains:

```ini
[pytest]
testpaths = src/tests
pythonpath = src
python_files = test_*.py
addopts = -v
```

### Missing Python Dependencies

Install them again:

```bash
py -m pip install -r requirements.txt
```

### `.env` Is Missing

Copy `.env.example` to `.env` and add the required development configuration values.

### Port 5173 Is Already In Use

Vite may select another available port automatically. Use the URL shown in your terminal.

---

## 12. Alpha Testing Scope

Our Alpha Development hypothesis is:

> The AI expense assistant generates an accurate expense split within 5 user prompts in at least 90% of attempts.

The testing plan includes:

- 3 development team members
- 6 predefined scenarios per person
- 18 total attempts
- Minimum 17 successful attempts to meet the 90% target

The six scenarios cover equal splits, exclusions, itemized expenses, unequal quantities with tax/tip, missing information, and typos or ambiguous instructions.

For full details, see `docs/AlphaTesting.md` and `docs/UserStories.md`.
