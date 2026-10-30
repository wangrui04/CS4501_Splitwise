# Splitwise AI — Alpha GitHub Issues (CS 4501)

## Project Overview

Splitwise AI is a shared-expense tracking application with a conversational AI assistant. Users describe expenses in natural language, and the application identifies participants, calculates individual shares, and provides an itemized preview for confirmation.

The Alpha Development phase focuses on implementing the core application, developing features using Test-Driven Development (TDD), and validating whether the AI can accurately interpret and split shared expenses.

This document contains the development plan for all 40 Alpha issues across two sprints.

---

## 1. Project Decisions

| Topic | Decision |
|---|---|
| Frontend | React + JavaScript, Vite |
| Backend | Python 3.11+ with FastAPI |
| Database | SQLite using Python's `sqlite3` |
| Data validation | Pydantic v2 |
| LLM | Anthropic Claude API |
| Backend testing | pytest |
| Property-based testing | Hypothesis |
| API testing | FastAPI TestClient |
| Frontend testing | React Testing Library where needed |
| End-to-end testing | Playwright |
| Money representation | Integer cents |
| Authentication | Name-based signed sessions |
| Alpha testing | 3 testers × 6 scenarios = 18 attempts |
| Success threshold | At least 17 of 18 attempts |
| Prompt limit | Maximum 5 user prompts |
| Development methodology | Test-Driven Development |

### Core Hypothesis

Our AI expense assistant can generate an accurate expense split within 5 user prompts in at least 90% of test attempts, across varying levels of complexity.

A successful test must produce the correct payer, participants, quantities, individual shares, and total.

### Architecture Principles

1. **LLM interprets, Python calculates.** The LLM extracts structured expense information. All calculations happen in Python.
2. **Integer-cent arithmetic.** Amounts are stored and calculated as integers, avoiding floating-point errors.
3. **Strict data validation.** All LLM outputs must pass Pydantic validation.
4. **Clarification instead of guessing.** Missing amounts, unknown participants, and ambiguous instructions trigger follow-up questions.
5. **User confirmation required.** No AI-generated expense is saved before validation and explicit confirmation.
6. **Mock external services during testing.** Automated tests do not make paid API calls.
7. **Manual entry remains available.** Users must be able to record an expense without the LLM.

### Rounding Rule

For every item or additional charge:

- Calculate each participant's exact fractional allocation.
- Floor each allocation to integer cents.
- Give remaining cents to the payer if the payer is a participant in that allocation.
- Otherwise, distribute remaining cents by largest fractional remainder, breaking ties using group roster order.
- Ensure the sum of shares equals the exact amount.

---

## 2. Repository Structure

Target structure:

```text
CS4501_Splitwise/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── allocation.py
│   ├── validator.py
│   ├── database.py
│   ├── repository.py
│   ├── llm.py
│   └── pipeline.py
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│   ├── test_setup.py
│   ├── test_expense.py
│   ├── test_validator.py
│   ├── test_backend.py
│   └── test_llm.py
│
├── benchmark/
│   ├── scenarios/
│   └── reports/
│
├── docs/
│   ├── AlphaTesting.md
│   ├── UserStories.md
│   ├── alpha_github_issues.md
│   └── prototype/
│
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

The repository will be migrated incrementally from its original HTML prototype.

The five main Python test files cover issues #1–12. Additional feature-specific and frontend tests may be added as development progresses.

---

## 3. GitHub Conventions

### Branch Naming

Branches follow the existing repository conventions:

```text
feature/<description>
fix/<description>
docs/<description>
```

Example:

```bash
git checkout -b feature/alpha-backend-core
```

### Commit Naming

Examples:

```text
test(ALPHA-05): Add expense allocation tests
feat(ALPHA-05): Implement expense allocation engine
fix(ALPHA-07): Correct validation of missing prices
docs(ALPHA-02): Align alpha testing documentation
```

### TDD Workflow

For each issue:

1. Write tests according to acceptance criteria.
2. Run tests to confirm they fail.
3. Commit the failing tests as TDD evidence.
4. Implement the minimum code necessary.
5. Run tests and verify they pass.
6. Refactor while keeping tests green.
7. Submit a pull request referencing the GitHub issue.

### Definition of Done

An issue is complete when:

- [ ] All acceptance criteria are satisfied.
- [ ] Required tests are implemented.
- [ ] Tests have passed.
- [ ] Any AI-generated tests have been reviewed by a team member.
- [ ] Changes have been reviewed.
- [ ] Relevant documentation is updated.
- [ ] No secrets or API keys have been committed.

### Labels

| Category | Labels |
|---|---|
| Type | `feature`, `bug`, `chore` |
| Sprint | `sprint-1`, `sprint-2` |
| Area | `frontend`, `backend`, `ai`, `testing`, `security`, `docs` |
| Priority | `P0`, `P1`, `P2` |
| Benchmark | `benchmark`, `tier-easy`, `tier-medium`, `tier-difficult` |
| Other | `optional` |

---

## 4. Sprint Plan

### Sprint 1 — October 29 to November 1

Goal: Establish the application architecture and deliver a working end-to-end expense-splitting flow.

### Sprint 2 — November 2 to November 4

Goal: Complete advanced expense scenarios, run the Alpha benchmark, and prepare the submission.

Submission deadline: November 5.

### Suggested Team Responsibilities

| Role | Responsibilities |
|---|---|
| A — Frontend | React, sign-in interface, expense forms, previews, group pages |
| B — Backend / LLM | FastAPI endpoints, sessions, Claude integration, conversation handling |
| C — QA / Validation | Pydantic schemas, allocation engine, validation, automated tests, benchmark |

Roles are suggestions. Actual issue ownership is determined by the team.

---

# SPRINT 1 — Foundation and Core Functionality

## ALPHA-01: Scaffold Python + React Project with pytest and CI

**Type:** Chore  
**Priority:** P0  
**Area:** Backend, Frontend, Testing  
**Estimate:** 2 hours  
**Dependencies:** None

### Description

Initialize the project structure with a Python FastAPI backend, React frontend, pytest testing infrastructure, and GitHub Actions CI.

### Acceptance Criteria

- [ ] Python backend is organized as an importable package.
- [ ] React frontend is initialized using Vite.
- [ ] `requirements.txt` lists the Python dependencies.
- [ ] `pytest.ini` configures pytest.
- [ ] `python -m pytest tests/ -v` runs the test suite.
- [ ] `.env.example` documents the required environment variables.
- [ ] `.env` is excluded through `.gitignore`.
- [ ] GitHub Actions runs backend tests on pull requests.
- [ ] README contains setup instructions.
- [ ] Original HTML prototype is preserved.
- [ ] PR template includes a TDD checklist.

### Testing

**File:** `tests/test_setup.py`

Verify project directories, dependencies, configuration files, documentation, and CI setup.

Add a FastAPI `/health` smoke test and a basic React rendering test when their implementations are ready.

---

## ALPHA-02: Align User Stories and Alpha Testing Documentation

**Type:** Chore  
**Priority:** P1  
**Area:** Documentation  
**Estimate:** 1.5 hours  
**Dependencies:** None

### Description

Make the user stories and Alpha testing plan consistent.

### Acceptance Criteria

- [ ] Alpha scope specifies 3 testers and 6 scenarios.
- [ ] Total test attempts equal 18.
- [ ] Minimum passing attempts equal 17.
- [ ] Hypothesis specifies 90% accuracy within 5 prompts.
- [ ] Remove outdated references to 10 students and 60 attempts from the Alpha plan.
- [ ] Update US-06 title to "Messy Language, Typos, and Unclear Instructions."
- [ ] Add US-07 manual entry.
- [ ] Add US-08 name-based sign-in.
- [ ] Add US-09 balances.
- [ ] Document optional US-10 corrections and US-11 itemized manual entry.
- [ ] Define prompt counting and scenario difficulty tiers.

### Testing

**File:** `tests/test_setup.py`

Check documentation consistency and required user-story references. Perform a manual review for accuracy.

---

## ALPHA-03: Confirm Alpha Validation Scope with Professor

**Type:** Chore  
**Priority:** P1  
**Area:** Documentation  
**Estimate:** 1 hour  
**Dependencies:** None

### Description

Confirm whether internal testing by the three team members satisfies the assignment's validation requirements.

### Acceptance Criteria

- [ ] Ask professor whether internal Alpha testing is sufficient.
- [ ] Document the response and confirmation date.
- [ ] If external testing is required, create a follow-up issue.
- [ ] Update the Alpha plan and attempt counts if necessary.
- [ ] State internal-testing limitations in the submission.

### Testing

**File:** `tests/test_setup.py`

Check that the decision record exists. Manually verify the recorded decision against the professor's actual response.

---

## ALPHA-04: Define Pydantic Expense Schemas

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI, Testing  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-01

### Description

Create shared Python data models used to validate structured LLM output and calculated expense previews.

### Required Schemas

**ParsedExpense**
- `description`
- `payer`
- `items`
- `charges`
- `statedTotal`
- `openQuestions`

Each item contains its name, quantity, unit price, and participant selection.

**ExpensePreview**
- `payer`
- `currency`
- `lineItems`
- `charges`
- `totalCents`
- `shares`
- `validated`

**ChatResponse**
- `question`
- `preview`
- `unresolved`
- `error`

### Acceptance Criteria

- [ ] Implement schemas using Pydantic v2.
- [ ] Reject unknown fields.
- [ ] Require positive integer item quantities.
- [ ] Validate decimal-string money amounts.
- [ ] Reject negative or malformed prices.
- [ ] Accept null payer or price for clarification.
- [ ] Reject LLM-generated `shares` and `totalCents`.
- [ ] Reject charges specifying both amount and percentage.
- [ ] Define structured response types.

### Testing

**File:** `tests/test_expense.py`

Test valid expenses, invalid quantities, malformed prices, unknown fields, null values, charge conflicts, and preview schemas.

---

## ALPHA-05: Implement Money Utilities and Expense Allocation

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, Testing  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-04

### Description

Implement deterministic Python functions for monetary conversion and expense allocation.

### Required Functions

```python
parse_money_to_cents()
format_cents()
resolve_participants()
allocate_items()
```

### Acceptance Criteria

- [ ] Convert decimal-string prices to integer cents.
- [ ] Support optional dollar-sign input.
- [ ] Reject negative amounts and invalid prices.
- [ ] Format cents as USD.
- [ ] Support `all`, `only`, and `all_except`.
- [ ] Resolve `ME` using the signed-in user.
- [ ] Reject names not in the group roster.
- [ ] Multiply item price by quantity.
- [ ] Support item-specific participant groups.
- [ ] Sum shares across multiple items.
- [ ] Never calculate monetary values using binary floating-point arithmetic.

### Testing

**File:** `tests/test_expense.py`

Test:

- $30 shared by Sarah, Kayla, and Rui → $10 each.
- $24 shared only by Kayla and Rui → $12 each.
- Different item allocations → Sarah $6, Kayla $21, Rui $15.
- Quantity 2 × $10 → $20.
- Unknown participant Ben in Apartment 4B → error.
- Everyone except Aly → Aly receives $0.

---

## ALPHA-06: Implement Deterministic Rounding

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, Testing  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-05

### Description

Ensure that shared expenses are divided into integer cents without losing or creating money.

### Required Function

```python
split_cents(amount_cents, weights, sharers, payer, roster_order)
```

### Acceptance Criteria

- [ ] Support equal splits.
- [ ] Support weighted splits.
- [ ] Apply the documented leftover-cent rule.
- [ ] Use roster order for tied remainders when payer is absent.
- [ ] Never return negative or fractional cents.
- [ ] Return deterministic results.
- [ ] Ensure total allocated cents equals the input amount.

### Testing

**File:** `tests/test_expense.py`

Test $10 among three participants, allocations of $0.01 and $0.02, weighted 1:2 splits, and randomized sum invariants using Hypothesis.

---

## ALPHA-07: Implement Deterministic Expense Validator

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, Security, Testing  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-04, ALPHA-05

### Description

Validate calculated expenses before displaying them as approved or saving them.

### Required Functions

```python
validate(parsed, allocation, roster)
question_for_error(error)
```

### Required Error Codes

- `SHARES_DONT_SUM`
- `NON_POSITIVE_TOTAL`
- `NEGATIVE_AMOUNT`
- `UNKNOWN_NAME`
- `MISSING_PAYER`
- `MISSING_PRICE`
- `NO_PARTICIPANTS`
- `TAX_TIP_METHOD_MISSING`
- `STATED_TOTAL_MISMATCH`
- `NON_INTEGER_CENTS`

### Acceptance Criteria

- [ ] Return `{ "ok": True }` for valid expenses.
- [ ] Return structured errors for invalid expenses.
- [ ] Validate payer and participants against the roster.
- [ ] Reject invalid or missing amounts.
- [ ] Validate item totals and additional charges.
- [ ] Ensure shares sum exactly to the expense total.
- [ ] Generate follow-up questions from validation errors.
- [ ] Never mark incorrect allocations as validated.

### Testing

**File:** `tests/test_validator.py`

Include a test for every error code, successful expense scenarios, mismatched totals, and property-based sum validation.

---

## ALPHA-08: Implement SQLite Database and Seed Data

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, Testing  
**Estimate:** 2.5 hours  
**Dependencies:** ALPHA-01, ALPHA-07

### Description

Create SQLite persistence for group membership, expenses, shares, and conversation state.

### Required Tables

- `groups`
- `group_members`
- `expenses`
- `expense_shares`
- `conversations`

Expense item details may be stored in a separate table or JSON column.

### Seed Data

**Apartment 4B:** Sarah, Kayla, Rui

**Weekend trip:** Sarah, Kayla, Rui, Aly, Ben

### Acceptance Criteria

- [ ] SQLite schema initializes successfully.
- [ ] Running seed operations multiple times creates no duplicates.
- [ ] Group members retain roster order.
- [ ] Support listing and retrieving groups.
- [ ] Save expense records and shares transactionally.
- [ ] Reject invalid expenses before saving.
- [ ] Roll back failed database