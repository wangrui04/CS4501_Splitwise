# Splitwise AI — Conversational Expense Assistant

**CS 4501: Software Engineering Final Project**

## Project Overview

Splitwise AI is a shared-expense tracking application inspired by Splitwise, with an AI-powered conversational assistant.

The application aims to help users record shared expenses, track group balances, and split complex bills through natural-language instructions instead of manually calculating each person's share.

For example:

> "I paid $42. Kayla and I shared $12 nachos. Rui had a $15 burger, and Kayla had a $15 pasta."

The assistant identifies the payer, items, prices, and participants to produce a structured expense breakdown.

If information is missing or unclear, the assistant asks follow-up questions rather than making assumptions.

**All monetary calculations are performed using deterministic Python code, not the LLM.** Expense allocations must pass validation and be confirmed by the user before they are saved.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, JavaScript, Vite |
| Backend | Python, FastAPI |
| Database | SQLite |
| AI Integration | Anthropic Claude API |
| Data Validation | Pydantic |
| Unit and Integration Testing | pytest |
| Property-Based Testing | Hypothesis |
| Version Control | Git and GitHub |
| Continuous Integration | GitHub Actions |

The intended architecture uses a React frontend communicating with a Python FastAPI backend through REST endpoints.

---

## Development Status

The project is currently in **Alpha Development**.

### Implemented and Tested

- React and Vite frontend project initialization
- FastAPI application and API endpoints
- SQLite database initialization and sample group data
- Expense allocation using integer cents
- Equal and itemized expense calculations
- Input validation and error handling
- Expense storage and retrieval
- Conversation record operations
- Name-based demo sessions and protected endpoints
- Signed session cookies
- Mock LLM implementation for deterministic testing
- Claude structured-output integration module
- Natural-language expense processing pipeline
- Automated tests for backend and LLM behavior
- GitHub Actions CI configuration

### In Progress / Planned

- Full React user interface
- Connecting React components to FastAPI endpoints
- Interactive AI expense-entry interface
- Expense preview and confirmation workflow in the frontend
- Group balance and expense history displays
- End-to-end testing with the live Claude API
- Alpha testing and collection of validation results

**Note:** Passing automated tests verifies the tested implementation. It does not yet establish the accuracy of the complete application with real users or live AI responses.

---

## Developer Setup

For installation instructions, environment configuration, local development, troubleshooting, and testing commands, see:

**[SETUP.md](SETUP.md)**

The guide covers:

- Installing Python, Node.js, and npm
- Cloning the repository
- Setting up the Python virtual environment
- Installing dependencies
- Configuring environment variables
- Running the React frontend
- Running automated tests

---

## Project Structure

The current development structure is:

```text
CS4501_Splitwise/
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   └── pull_request_template.md
│
├── docs/
│   ├── AlphaTesting.md
│   ├── UserStories.md
│   └── alpha-validation-decision.md
│
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│
├── src/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── allocation.py
│   │   ├── validator.py
│   │   ├── database.py
│   │   ├── repository.py
│   │   ├── llm.py
│   │   └── pipeline.py
│   │
│   ├── demo/
│   │   └── splitwise_ai_demo.html
│   │
│   └── tests/
│       ├── test_setup.py
│       ├── test_expense.py
│       ├── test_validator.py
│       ├── test_backend.py
│       └── test_llm.py
│
├── ideas/
├── AGENTS.md
├── README-startupSelected.md
├── README.md
├── SETUP.md
├── requirements.txt
├── pytest.ini
├── .env.example
└── .gitignore
```

The original HTML prototype is preserved in `src/demo/` as a reference for frontend development.

The React interface is being developed separately in `frontend/`.

---

## Core Features

### 1. Conversational Expense Entry

Users can describe shared expenses in natural language.

The AI assistant is designed to extract:

- Payer
- Purchased items and quantities
- Individual item prices
- Participants
- Excluded group members
- Tax, tip, and additional charges
- Instructions for splitting expenses

The extracted information is converted into structured data for further validation and calculation.

### 2. Expense Splitting

The Python allocation engine calculates each person's share.

Supported calculation scenarios include:

- Equal splitting
- Splitting among selected participants
- Itemized expenses with different participants
- Different item quantities
- Participant exclusions
- Equal or proportional allocation of additional charges

All calculations use integer cents to avoid floating-point rounding errors.

The sum of individual shares must equal the full expense total.

### 3. Clarification Questions

The assistant is designed to ask questions when information is missing, contradictory, or ambiguous.

Examples include:

- "Who paid for this expense?"
- "How much were the nachos?"
- "Did you mean Rui?"
- "Should the tip be split equally or proportionally?"

The conversation pipeline retains previous messages so users do not need to restate their entire expense.

### 4. Expense Validation

The backend validates expenses before saving.

Validation includes checking that:

- The payer belongs to the selected group.
- Participants are valid group members.
- Monetary amounts are valid.
- Individual shares are nonnegative integer amounts in cents.
- No participants are duplicated incorrectly.
- Individual shares add up to the expense total.
- Required information is present.

Invalid expenses are rejected rather than permanently stored.

### 5. Expense Preview and Confirmation

The intended user workflow is:

1. The user enters an expense manually or through the AI assistant.
2. The application calculates the allocation.
3. The backend validates the result.
4. The frontend displays an itemized breakdown.
5. The user reviews and confirms the breakdown.
6. The confirmed expense is saved.

The frontend implementation of this workflow is part of ongoing Alpha development.

### 6. Groups and Expense History

SQLite stores information about groups, members, expenses, individual shares, and conversations.

The Alpha prototype includes two sample groups.

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

These predefined groups allow the development team to test expense allocation and group management consistently.

### 7. Name-Based Demo Sessions

For the Alpha prototype, users can select their name from a predefined group-member roster.

The backend creates a signed session and protects group-related API endpoints.

This approach is intended for an internal demonstration and is not a replacement for production authentication.

---

## Alpha Development Hypothesis

Our core hypothesis is:

**The AI expense assistant can generate an accurate expense split within 5 user prompts in at least 90% of test attempts across varying levels of complexity.**

### Alpha Testing Plan

| Metric | Target |
|---|---|
| Testers | 3 development team members |
| Scenarios | 6 |
| Attempts per tester | 6 |
| Total attempts | 18 |
| Required successful attempts | 17 |
| Accuracy target | At least 90% |
| Prompt limit | 5 user prompts |

An attempt is considered successful only when the assistant correctly identifies the payer, items, participants, individual shares, and total within five user prompts.

### Six Testing Scenarios

1. Equal expense splitting
2. Splitting among selected members
3. Itemized expenses with different participants
4. Unequal quantities with tax/tip allocation
5. Missing or ambiguous information
6. Typos and unclear natural-language instructions

The Alpha testing plan uses internal team members to evaluate initial functionality.

External user validation may be performed in a later development stage, subject to course requirements and professor guidance.

See [AlphaTesting.md](docs/AlphaTesting.md) and [UserStories.md](docs/UserStories.md) for more details.

---

## Test-Driven Development

The project follows a **Red–Green–Refactor** development cycle.

### Red — Write Failing Tests

Tests are written based on the acceptance criteria of each GitHub issue.

They are run before implementation to verify the required behavior is not yet satisfied.

### Green — Implement the Feature

The minimum necessary functionality is implemented until the tests pass.

### Refactor — Improve the Implementation

The code is improved for readability, structure, and maintainability while keeping tests passing.

### Running Tests

From the repository root:

```bash
py -m pytest src/tests/ -v --tb=short
```

For macOS/Linux, use the appropriate Python command, such as:

```bash
python3 -m pytest src/tests/ -v --tb=short
```

To run an individual test module:

```bash
py -m pytest src/tests/test_backend.py -v
```

### Test Organization

| Test File | Coverage |
|---|---|
| `test_setup.py` | Project structure, dependencies, configuration, and documentation |
| `test_expense.py` | Expense models, allocation, rounding, and edge cases |
| `test_validator.py` | Validation of expense data and allocations |
| `test_backend.py` | Database, persistence, groups, sessions, and API endpoints |
| `test_llm.py` | Mock LLM, Claude integration, retries, and conversation processing |

### Latest Local Test Results

As of October 31, 2026:

**121 tests passed.**

These results were obtained through the local pytest suite. Live Claude API accuracy and complete frontend-to-backend workflows require separate validation.

The repository also includes a GitHub Actions workflow to run Python tests automatically on pushes and pull requests.

---

## AI Integration Architecture

The AI assistant is responsible for interpreting natural-language expense descriptions.

It is not responsible for performing the final financial calculations.

The intended processing pipeline is:

```text
User enters expense description
             |
             v
    Anthropic Claude API
             |
             v
 Structured expense information
             |
             v
    Pydantic validation
             |
             v
  Python allocation engine
             |
             v
   Allocation validation
             |
             v
      Expense preview
             |
             v
      User confirmation
             |
             v
        SQLite database
```

The automated tests use a fake LLM implementation to validate the pipeline without requiring live API calls.

The actual performance of Claude on the six Alpha scenarios must be evaluated separately.

---

## Development Workflow

The team uses GitHub issues to organize feature development and testing requirements.

Recommended workflow:

1. Select an assigned GitHub issue.
2. Create a feature branch.
3. Write tests based on the acceptance criteria.
4. Confirm the tests initially fail.
5. Implement the required functionality.
6. Run the relevant tests.
7. Refactor as necessary.
8. Open a pull request.
9. Request teammate review before merging.

Before submitting a pull request, developers should verify that:

- Relevant tests pass.
- Changes satisfy the linked GitHub issue.
- No sensitive credentials are included.
- AI-generated code has been reviewed.
- Documentation is updated when necessary.

---

## Security and Environment Variables

The project uses environment variables for development configuration.

Required configuration variables are documented in `.env.example`:

```env
ANTHROPIC_API_KEY=
LLM_MODEL=
SESSION_SECRET=
```

Actual values belong in a local `.env` file.

**Never commit real API keys, passwords, or session secrets to GitHub.**

Automated LLM tests use mock responses and do not require a live Anthropic API key.

For setup and environment configuration, refer to [SETUP.md](SETUP.md).

---

## Future Development

Planned work includes:

- Completing the React interface
- Connecting frontend components to backend endpoints
- Integrating the live Claude assistant into the user experience
- Supporting complete expense preview and confirmation workflows
- Displaying group balances and expense history
- Running end-to-end Alpha scenarios
- Recording accuracy and prompt-count metrics
- Improving the application based on testing results

---

## Project Documentation

- [Developer Setup](SETUP.md)
- [Alpha Testing Plan](docs/AlphaTesting.md)
- [User Stories](docs/UserStories.md)
- [Alpha Validation Decision](docs/alpha-validation-decision.md)

Additional planning and development tasks are tracked through GitHub issues.

---

## Course Information

**Course:** CS 4501 — Software Engineering  
**Project:** Splitwise AI — Conversational Expense Assistant  
**Development Stage:** Alpha Development