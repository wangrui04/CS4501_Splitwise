# Splitwise AI — Conversational Expense Assistant

CS 4501: Software Engineering Final Project

## Project Overview

Splitwise AI is a shared-expense tracking application inspired by Splitwise, with an additional AI-powered conversational assistant.

The application allows users to record shared expenses, calculate how much each group member owes, and describe complex bills using natural language instead of manually calculating individual shares.

For example:

> "I paid $42. Kayla and I shared $12 nachos. Rui had a $15 burger, and Kayla had a $15 pasta."

The assistant identifies the payer, items, prices, and participants, then calculates each person's share.

If information is missing or unclear, the assistant asks follow-up questions rather than making assumptions.

All calculations are performed using deterministic Python code, not the LLM. Expenses must be validated and confirmed before they are saved.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, JavaScript |
| Backend | Python, FastAPI |
| Database | SQLite |
| AI Integration | Anthropic Claude API |
| Data Validation | Pydantic |
| Unit and Integration Testing | pytest |
| Property-Based Testing | Hypothesis |
| Version Control | Git and GitHub |

The frontend communicates with the Python backend through REST API endpoints.

## Project Structure

The following is the target project structure as the Alpha implementation is developed:

```text
CS4501_Splitwise/
│
├── backend/
│   ├── __init__.py
│   ├── main.py             # FastAPI application and routes
│   ├── schemas.py          # Pydantic data models
│   ├── allocation.py       # Expense calculations and rounding
│   ├── validator.py        # Expense validation
│   ├── database.py         # SQLite initialization and seed data
│   ├── repository.py       # Database operations
│   ├── llm.py              # Claude integration and mock LLM
│   └── pipeline.py         # Natural-language parsing pipeline
│
├── frontend/               # React application
│
├── tests/
│   ├── test_setup.py       # Issues #1-3
│   ├── test_expense.py     # Issues #4-6
│   ├── test_validator.py   # Issue #7
│   ├── test_backend.py     # Issues #8-9
│   └── test_llm.py         # Issues #10-12
│
├── docs/
│   ├── AlphaTesting.md
│   ├── UserStories.md
│   ├── alpha_github_issues.md
│   └── mvp-issues.md
│
├── ideas/                  # Initial startup proposals
│
├── src/
│   └── splitwise_ai_demo.html
│
├── AGENTS.md
├── README-startupSelected.md
├── README.md
├── requirements.txt
├── pytest.ini
├── .env.example
└── .gitignore
```

The original HTML prototype is retained as a reference for frontend development. GitHub issue #1 proposes moving it to `docs/prototype/`.

Some files in this structure are still planned or under development and may not yet exist on the main branch.

---

## Core Features

### 1. Conversational Expense Entry

Users can describe shared expenses using natural language.

The AI assistant extracts:

- Payer
- Purchased items and quantities
- Individual item prices
- Participants
- Excluded group members
- Tax, tip, and additional charges

### 2. Expense Splitting

The Python allocation engine calculates each person's share.

Supported splitting behaviors include:

- Equal splits
- Splits among selected members
- Different participants for different items
- Multiple quantities
- Participant exclusions
- Equal or proportional distribution of additional charges

All monetary calculations use integer cents to avoid floating-point rounding errors.

### 3. Clarification Questions

The assistant asks questions when information is missing or ambiguous.

Examples:

- "Who paid for this expense?"
- "How much were the nachos?"
- "Did you mean Rui?"
- "Should the tip be split equally or proportionally?"

The assistant should retain information from earlier messages instead of requiring users to repeat the entire expense.

### 4. Expense Validation

Before an expense can be saved, the backend checks:

- All participants belong to the group.
- The payer is valid.
- Item prices and quantities are valid.
- Tax and tip allocation methods are specified.
- Every share is a nonnegative integer number of cents.
- All individual shares add up to the total.
- No required information is missing.

Invalid expenses must not be saved.

### 5. Expense Preview and Confirmation

After calculation and validation, the application displays an itemized breakdown showing how much each participant owes.

The user must confirm the preview before the expense is permanently saved.

### 6. Groups and Expense History

The application uses SQLite to store group members, expenses, individual shares, and conversation records.

The Alpha prototype includes two sample groups:

**Apartment 4B**
- Sarah
- Kayla
- Rui

**Weekend Trip**
- Sarah
- Kayla
- Rui
- Aly
- Ben

---

## Alpha Development Hypothesis

Our core hypothesis is:

**The AI expense assistant can generate an accurate expense split within 5 user prompts in at least 90% of test attempts across varying levels of complexity.**

### Alpha Testing Plan

| Metric | Target |
|---|---|
| Testers | 3 team members |
| Scenarios | 6 |
| Attempts per tester | 6 |
| Total attempts | 18 |
| Required successful attempts | 17 |
| Accuracy threshold | At least 90% |
| Prompt limit | 5 user prompts |

An attempt is successful only when the correct payer, items, participants, individual amounts, and total are identified within five user messages.

The six scenario categories cover simple equal splits, selected participants, itemized expenses, unequal quantities, missing information, and ambiguous or misspelled instructions.

The Alpha evaluation uses internal team testing. External user validation is a future step.

See [docs/AlphaTesting.md](docs/AlphaTesting.md) for the detailed testing plan.

---

## Getting Started

### Prerequisites

Install:

- Python 3.11 or newer
- Node.js and npm
- Git
- Visual Studio Code or another code editor

### 1. Clone the Repository

```bash
git clone https://github.com/wangrui04/CS4501_Splitwise.git
cd CS4501_Splitwise
```

### 2. Set Up the Python Backend

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a reference.

```env
ANTHROPIC_API_KEY=your_api_key_here
LLM_MODEL=your_supported_model_id
SESSION_SECRET=your_random_secret
```

Never commit the `.env` file or share real API keys.

Automated tests use mocked LLM responses and do not require a real Claude API key.

### 4. Start the Backend

Once the backend entry point is implemented, start the FastAPI application using Uvicorn.

The application factory currently accepts a database connection and session secret, so a local development entry point will need to initialize these dependencies before the server can start.

Once configured, the API can run locally at:

```text
http://localhost:8000
```

FastAPI's generated API documentation is available at:

```text
http://localhost:8000/docs
```

### 5. Start the React Frontend

Once the React project is initialized:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by the development server.

The frontend should send API requests to the Python backend.

---

## Test-Driven Development

We follow the Red-Green-Refactor development cycle.

### Red — Write Failing Tests

Write automated tests based on each GitHub issue's acceptance criteria before implementing the functionality.

Run the tests and record the failures.

### Green — Implement the Feature

Write the minimum code necessary to make the tests pass.

### Refactor — Improve the Implementation

Improve code readability, structure, and maintainability while keeping the tests passing.

### Running Tests

Run