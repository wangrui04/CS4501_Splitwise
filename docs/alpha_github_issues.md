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
- [ ] Roll back failed database operations.
- [ ] Support conversation CRUD operations.
- [ ] Use in-memory SQLite databases during testing.

### Testing

**File:** `tests/test_backend.py`

Verify seed data, group rosters, persistence, invalid-save rejection, transactions, and conversation CRUD.

---

## ALPHA-09: Implement Name-Based Sessions and Group Endpoints

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, Security, Testing  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-01, ALPHA-08

### User Story

As a group member, I want to sign in by selecting my name so that "I" and "me" refer to me in conversations.

### Required Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/session/names` | Available names |
| POST | `/api/session` | Sign in |
| GET | `/api/session` | Current user |
| DELETE | `/api/session` | Sign out |
| GET | `/api/groups` | List groups |
| GET | `/api/groups/{id}` | Group details |

### Acceptance Criteria

- [ ] Implement endpoints with FastAPI.
- [ ] Accept only seeded names.
- [ ] Store user identity in a signed session cookie.
- [ ] Use HttpOnly and SameSite=Lax cookie settings.
- [ ] Reject requests without a valid session.
- [ ] Reject tampered cookies.
- [ ] Read the authenticated user from the session, not request data.
- [ ] Protect all non-public API endpoints.
- [ ] Sign-out clears the session.
- [ ] Do not require passwords for the Alpha prototype.

### Testing

**File:** `tests/test_backend.py`

Use FastAPI TestClient to verify login, logout, cookies, identity handling, groups, and protected routes.

---

## ALPHA-10: Build Mock LLM Harness and Scenario Fixtures

**Type:** Chore  
**Priority:** P0  
**Area:** AI, Testing  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-04

### Description

Create deterministic mock LLM responses for automated tests.

### Acceptance Criteria

- [ ] Define a common LLM client interface.
- [ ] Implement `FakeLlmClient`.
- [ ] Support scripted LLM responses.
- [ ] Record inputs for inspection during tests.
- [ ] Raise a controlled error when scripted responses are exhausted.
- [ ] Define fixtures for all six Alpha scenarios.
- [ ] Include intermediate clarification turns.
- [ ] Validate fixture data with Pydantic.
- [ ] Ensure automated tests never call the real Claude API.
- [ ] Optional recording mode stores sanitized real outputs for regression tests.

### Testing

**File:** `tests/test_llm.py`

Verify scripted response order, exhaustion behavior, call recording, schema validity, and network isolation.

---

## ALPHA-11: Implement Claude Client with Structured Output

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI, Security, Testing  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-04, ALPHA-10

### Description

Implement a Python wrapper around the Anthropic API that returns structured expense data.

### Acceptance Criteria

- [ ] API key is loaded from server environment variables.
- [ ] Model identifier is configurable through `LLM_MODEL`.
- [ ] Use supported deterministic generation settings.
- [ ] Request structured tool output.
- [ ] Reject text-only responses.
- [ ] Validate tool output using Pydantic.
- [ ] Retry invalid structured output once with validation feedback.
- [ ] Retry transient network failures once.
- [ ] Configure a request timeout.
- [ ] Return a controlled error when retries fail.
- [ ] Never expose API keys in frontend code, logs, or responses.
- [ ] Provide a manual live-API smoke test outside CI.

### Testing

**File:** `tests/test_llm.py`

Mock the Anthropic SDK to verify valid responses, invalid output retries, model configuration, forced tool use, network failures, and API-key safety.

---

## ALPHA-12: Implement Natural-Language Expense Parsing Pipeline

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI, Testing  
**Estimate:** 4 hours  
**Dependencies:** ALPHA-05, ALPHA-06, ALPHA-07, ALPHA-10

### User Story

As a user, I want to describe an expense naturally so that the application calculates who owes what without requiring manual calculations.

### Required Function

```python
parse_turn(llm, conversation, roster, current_user)
```

### Description

Connect the LLM interpretation, deterministic allocation engine, and validator.

### Acceptance Criteria

- [ ] Send full conversation history to the LLM.
- [ ] Include group roster and signed-in user context.
- [ ] Extract structured expense information.
- [ ] Resolve `ME` and participant rules.
- [ ] Calculate shares using Python.
- [ ] Validate the calculated allocation.
- [ ] Return clarification questions when required.
- [ ] Never invent missing prices or payer information.
- [ ] Never show invalid previews.
- [ ] Return validated previews for US-01, US-02, and US-03.
- [ ] Keep the system prompt versioned and configurable.

### Testing

**File:** `tests/test_llm.py`

Test equal splits, selected participants, itemized allocations, missing information, unknown names, first-person references, invalid LLM fields, and multi-turn context retention.

---

## ALPHA-13: Add Chat Orchestration Endpoint

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI  
**Estimate:** 3.5 hours  
**Dependencies:** ALPHA-09, ALPHA-12

### Description

Expose the expense parsing pipeline through a conversational API.

### Acceptance Criteria

- [ ] Implement a protected chat endpoint.
- [ ] Create and retrieve conversation records.
- [ ] Append user and assistant messages.
- [ ] Maintain full conversation context.
- [ ] Count each user message as one prompt.
- [ ] Return questions or validated previews.
- [ ] Mark attempts exceeding five prompts as unsuccessful for benchmarking.
- [ ] Provide a manual-entry fallback when unresolved.
- [ ] Never save unconfirmed expenses.

### Testing

Mock the LLM and test prompt counting, conversation persistence, clarification turns, unresolved responses, and session protection.

---

## ALPHA-14: Add Confirm Endpoint and Save Guardrail

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, Security  
**Estimate:** 2.5 hours  
**Dependencies:** ALPHA-08, ALPHA-12, ALPHA-13

### Description

Save a validated expense only when the user explicitly confirms the preview.

### Acceptance Criteria

- [ ] Implement an expense-confirmation endpoint.
- [ ] Retrieve the server-side draft.
- [ ] Recompute and revalidate the allocation.
- [ ] Reject invalid or unresolved drafts.
- [ ] Never trust client-supplied totals or shares.
- [ ] Save validated shares transactionally.
- [ ] Prevent accidental duplicate confirmation.
- [ ] Ensure unconfirmed previews do not change balances.

### Testing

Test valid confirmation, invalid drafts, manipulated totals, duplicate confirmation, and unchanged balances before confirmation.

---

## ALPHA-15: Scaffold React Application

**Type:** Feature  
**Priority:** P0  
**Area:** Frontend  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-01

### Acceptance Criteria

- [ ] Initialize React with Vite and JavaScript.
- [ ] Implement application layout and navigation.
- [ ] Add a sidebar with groups.
- [ ] Add group page structure.
- [ ] Support loading and error states.
- [ ] Preserve the original prototype's general layout.
- [ ] Configure local communication with FastAPI.
- [ ] Use reusable components.

### Testing

React Testing Library tests for basic rendering, navigation, group selection, and loading states.

---

## ALPHA-16: Build Name-Picker Sign-In Screen

**Type:** Feature  
**Priority:** P0  
**Area:** Frontend  
**Estimate:** 1.5 hours  
**Dependencies:** ALPHA-09, ALPHA-15

### Acceptance Criteria

- [ ] Fetch available names.
- [ ] Display a name-picker interface.
- [ ] Sign in through the backend.
- [ ] Display the signed-in user's name.
- [ ] Support sign-out and switching users.
- [ ] Handle unsuccessful login attempts.
- [ ] Persist user identity through server sessions.

### Testing

Test sign-in, sign-out, invalid selections, session restoration, and switching users.

---

## ALPHA-17: Build Add-Expense Modal with AI Chat

**Type:** Feature  
**Priority:** P0  
**Area:** Frontend, AI  
**Estimate:** 3.5 hours  
**Dependencies:** ALPHA-13, ALPHA-15

### Acceptance Criteria

- [ ] Add an expense-entry modal.
- [ ] Include AI and manual entry options.
- [ ] Provide a chat input.
- [ ] Display message history.
- [ ] Display clarification questions.
- [ ] Show loading and error states.
- [ ] Display the current prompt count.
- [ ] Connect the interface to the backend chat endpoint.

### Testing

Test message submission, response rendering, clarification handling, prompt counts, and API failures.

---

## ALPHA-18: Build Itemized Preview and Confirmation

**Type:** Feature  
**Priority:** P0  
**Area:** Frontend  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-14, ALPHA-17

### Acceptance Criteria

- [ ] Display payer and expense description.
- [ ] Display itemized expenses.
- [ ] Display every participant's share.
- [ ] Display tax and tip where applicable.
- [ ] Show the total.
- [ ] Show Confirm and Cancel actions.
- [ ] Confirm only validated previews.
- [ ] Never update balances before confirmation.
- [ ] Display success or error feedback after confirmation.

### Testing

Test preview rendering, confirmation, cancellation, invalid previews, and duplicate submissions.

---

## ALPHA-19: Deliver US-01 Equal Splitting End-to-End

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI, Testing  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-12, ALPHA-14, ALPHA-18

### Scenario

"I paid $30 for dinner for Sarah, Kayla, and Rui. Split it equally."

### Expected Result

| Person | Share |
|---|---:|
| Sarah | $10.00 |
| Kayla | $10.00 |
| Rui | $10.00 |
| Total | $30.00 |

### Acceptance Criteria

- [ ] Correct payer identified.
- [ ] All participants identified.
- [ ] Exact equal split calculated.
- [ ] Preview displayed.
- [ ] Confirmation saves the expense.
- [ ] Completed within five prompts.

### Testing

End-to-end test using a mocked LLM, with assertions against saved database shares.

---

## ALPHA-20: Deliver US-02 Selected-Member Splitting

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI, Testing  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-19

### Scenario

"I paid $24 for groceries, but only Kayla and Rui are sharing them."

### Expected Result

| Person | Share |
|---|---:|
| Sarah | $0.00 |
| Kayla | $12.00 |
| Rui | $12.00 |

### Acceptance Criteria

- [ ] Only specified participants are charged.
- [ ] Nonparticipants receive zero.
- [ ] Total remains correct.
- [ ] Preview is validated and confirmed.
- [ ] Completed within five prompts.

### Testing

Test correct inclusion, exclusion, and saved shares.

---

# SPRINT 2 — Advanced Features and Validation

## ALPHA-21: Add Tax and Tip Allocation

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, Testing  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-05, ALPHA-06

### Acceptance Criteria

- [ ] Support fixed tax, tip, and fee amounts.
- [ ] Support percentage-based charges.
- [ ] Support equal allocation.
- [ ] Support proportional allocation using item subtotals.
- [ ] Ask for clarification when the method is missing.
- [ ] Apply deterministic rounding.
- [ ] Ensure total shares match the full bill.

### Testing

Unit tests for equal and proportional tax/tip distribution, missing methods, and rounding.

---

## ALPHA-22: Deliver US-03 Itemized Multi-Way Splitting

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-12, ALPHA-19

### Scenario

"I paid $42. Kayla and I shared $12 nachos. Rui had a $15 burger, and Kayla had a $15 pasta."

### Expected Result

- Sarah: $6
- Kayla: $21
- Rui: $15

### Acceptance Criteria

- [ ] Multiple items identified.
- [ ] Item-specific participant groups handled.
- [ ] Correct allocation generated.
- [ ] Total equals $42.
- [ ] Itemized preview displayed.
- [ ] Completed within five prompts.

### Testing

Test complete scenario through the parsing pipeline and database.

---

## ALPHA-23: Deliver US-04 Quantities and Tax/Tip

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI  
**Estimate:** 3.5 hours  
**Dependencies:** ALPHA-21, ALPHA-22

### Scenario

"Kayla got two $10 drinks, Rui got one $10 drink, and I didn't have anything. The tip was $6. Split the tip proportionally."

### Expected Result

- Sarah: $0
- Kayla: $24
- Rui: $12
- Total: $36

### Acceptance Criteria

- [ ] Item quantities handled.
- [ ] Tip distribution follows the requested method.
- [ ] Correct total generated.
- [ ] Payer does not automatically owe an item share.
- [ ] Completed within five prompts.

### Testing

Test quantities, proportional charges, payer handling, and correct totals.

---

## ALPHA-24: Deliver US-05 Missing Information Handling

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI  
**Estimate:** 4 hours  
**Dependencies:** ALPHA-12, ALPHA-13

### Acceptance Criteria

- [ ] Missing prices trigger questions.
- [ ] Missing payer triggers a question.
- [ ] Missing participant information triggers a question.
- [ ] No values are invented.
- [ ] Previous conversation details are retained.
- [ ] Clarification responses update the parsed expense.
- [ ] Accurate preview is generated within five prompts when enough information is provided.
- [ ] Unresolved expenses cannot be saved.

### Testing

Mock multi-turn conversations and verify correct allocations after clarification.

---

## ALPHA-25: Deliver US-06 Typos and Unclear Instructions

**Type:** Feature  
**Priority:** P0  
**Area:** Backend, AI  
**Estimate:** 4 hours  
**Dependencies:** ALPHA-24

### Scenario

"I paid for dinr. Me and Kayla shared nachoes for $16. Riu got 2 drnks for $5 each. Split the rest evenly."

### Acceptance Criteria

- [ ] Recognize obvious item-name typos.
- [ ] Resolve unambiguous misspelled member names.
- [ ] Ask about unclear instructions such as "the rest."
- [ ] Avoid guessing ambiguous participant names.
- [ ] Retain previous details.
- [ ] Produce the correct split after clarification.
- [ ] Validate the preview.
- [ ] Complete within five prompts.

### Testing

Test typos, ambiguous descriptions, clarification handling, and preserved conversation context.

---

## ALPHA-26: Implement Manual Expense Entry Endpoint

**Type:** Feature  
**Priority:** P1  
**Area:** Backend  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-08, ALPHA-14

### Acceptance Criteria

- [ ] Accept manually entered expense details.
- [ ] Support equal splitting among selected participants.
- [ ] Use the same allocation and validation functions as AI-generated expenses.
- [ ] Reject invalid amounts and members.
- [ ] Require confirmation before saving.
- [ ] Record the expense source as manual.

### Testing

Test valid manual expenses, invalid input, and confirmation-gated persistence.

---

## ALPHA-27: Build Manual Expense Form

**Type:** Feature  
**Priority:** P1  
**Area:** Frontend  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-17, ALPHA-26

### Acceptance Criteria

- [ ] Allow manual description entry.
- [ ] Allow payer selection.
- [ ] Allow amount entry.
- [ ] Allow participant selection.
- [ ] Show equal-split preview.
- [ ] Display validation errors.
- [ ] Support confirmation and cancellation.

### Testing

Test form input, calculations, submission, and error handling.

---

## ALPHA-28: Implement Balances and Group Summary API

**Type:** Feature  
**Priority:** P1  
**Area:** Backend  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-08, ALPHA-14

### Acceptance Criteria

- [ ] Calculate how much each member paid.
- [ ] Calculate each member's allocated share.
- [ ] Determine net balances.
- [ ] Return group expense history.
- [ ] Exclude unconfirmed drafts.
- [ ] Ensure total net balances sum to zero.

### Testing

Test multiple expenses, different payers, balance conservation, and unconfirmed drafts.

---

## ALPHA-29: Build Group Summary and Balances UI

**Type:** Feature  
**Priority:** P1  
**Area:** Frontend  
**Estimate:** 3.5 hours  
**Dependencies:** ALPHA-28

### Acceptance Criteria

- [ ] Display group members.
- [ ] Display expense history.
- [ ] Display total group expenses.
- [ ] Show individual balances.
- [ ] Display who owes and who is owed.
- [ ] Refresh data after confirmed expenses.
- [ ] Support empty states.

### Testing

Test expense-list rendering and balance updates.

---

## ALPHA-30: Add Manual Fallback for Unresolved Chats

**Type:** Feature  
**Priority:** P1  
**Area:** Frontend, AI  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-17, ALPHA-27

### Acceptance Criteria

- [ ] Detect unresolved conversations.
- [ ] Provide an option to switch to manual entry.
- [ ] Preserve available expense details where safe.
- [ ] Never automatically save invalid previews.
- [ ] Clearly explain when AI parsing fails.

### Testing

Test fallback behavior and unsaved expense handling.

---

## ALPHA-31: Build Automated Benchmark Runner

**Type:** Feature  
**Priority:** P0  
**Area:** Testing, AI  
**Estimate:** 4 hours  
**Dependencies:** ALPHA-19 through ALPHA-25

### Description

Evaluate the AI assistant against six predefined scenarios.

### Acceptance Criteria

- [ ] Define six scenario fixtures with answer keys.
- [ ] Run the real LLM only when explicitly requested.
- [ ] Track the number of user prompts.
- [ ] Compare payer and individual shares against expected results.
- [ ] Require exact cent-level accuracy.
- [ ] Record successful and unsuccessful attempts.
- [ ] Support three consistency runs.
- [ ] Export benchmark results.
- [ ] Keep real API calls out of CI.

### Testing

Test the benchmark scoring logic with mocked model responses.

---

## ALPHA-32: Generate Benchmark Report

**Type:** Feature  
**Priority:** P1  
**Area:** Testing, Documentation  
**Estimate:** 2.5 hours  
**Dependencies:** ALPHA-31

### Acceptance Criteria

- [ ] Report Run 1, Run 2, and Run 3 separately.
- [ ] Calculate overall accuracy.
- [ ] Report results by scenario difficulty.
- [ ] Record prompt counts.
- [ ] Identify failure types.
- [ ] Explain that 5/6 is below 90%.
- [ ] Distinguish automated benchmark results from the 18-attempt human test session.

### Testing

Test report calculations and formatting using known results.

---

## ALPHA-33: Run Alpha Testing Session

**Type:** Chore  
**Priority:** P0  
**Area:** Testing, Documentation  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-31, ALPHA-32

### Description

Conduct internal Alpha validation using the three team members.

### Acceptance Criteria

- [ ] Each team member completes six scenarios.
- [ ] Record 18 total attempts.
- [ ] Record expected and actual allocations.
- [ ] Record user prompt counts.
- [ ] Record failures and error categories.
- [ ] Calculate overall accuracy.
- [ ] Determine whether at least 17 attempts passed.
- [ ] Document testing limitations.
- [ ] Include results in the Alpha submission.

### Testing

Manual validation against predetermined answer keys. Results must be recorded rather than simulated.

---

## ALPHA-34: Add Rate Limiting and Prompt-Injection Safeguards

**Type:** Chore  
**Priority:** P1  
**Area:** Backend, AI, Security  
**Estimate:** 2 hours  
**Dependencies:** ALPHA-11, ALPHA-13

### Acceptance Criteria

- [ ] Limit excessive chat requests.
- [ ] Reject excessively large inputs.
- [ ] Keep system instructions separate from user messages.
- [ ] Prevent user instructions from bypassing structured-output requirements.
- [ ] Ensure the LLM cannot directly save or modify expenses.
- [ ] Protect API keys and error messages.
- [ ] Handle model failures gracefully.

### Testing

Mock malicious or malformed messages and verify that validation and confirmation safeguards remain enforced.

---

## ALPHA-35: Verify First-Person References Across Users

**Type:** Chore  
**Priority:** P1  
**Area:** Backend, AI, Testing  
**Estimate:** 1.5 hours  
**Dependencies:** ALPHA-09, ALPHA-12

### Acceptance Criteria

- [ ] `ME` resolves to Sarah when Sarah is signed in.
- [ ] `ME` resolves to Kayla when Kayla is signed in.
- [ ] `ME` resolves to Rui when Rui is signed in.
- [ ] The request body cannot override session identity.
- [ ] Conversations are associated with the correct user.

### Testing

Parameterized pytest tests for all three signed-in users.

---

## ALPHA-36: Add End-to-End Smoke Tests

**Type:** Chore  
**Priority:** P2  
**Area:** Frontend, Testing  
**Estimate:** 3 hours  
**Dependencies:** ALPHA-18, ALPHA-29

### Acceptance Criteria

- [ ] Verify application loads.
- [ ] Verify sign-in.
- [ ] Verify group selection.
- [ ] Verify expense entry.
- [ ] Verify clarification handling.
- [ ] Verify preview display.
- [ ] Verify confirmation.
- [ ] Verify saved expense appears in history.
- [ ] Verify unconfirmed expenses do not change balances.

### Testing

Playwright browser tests, with external LLM calls mocked.

---

## ALPHA-37: Prepare Alpha Submission

**Type:** Chore  
**Priority:** P0  
**Area:** Documentation  
**Estimate:** 4 hours  
**Dependencies:** Main Alpha features and testing session

### Acceptance Criteria

- [ ] Update README.
- [ ] Update Alpha testing documentation.
- [ ] Ensure GitHub issues link to user stories.
- [ ] Include test evidence.
- [ ] Include failing and passing test examples.
- [ ] Include benchmark results.
- [ ] Explain architecture and design decisions.
- [ ] Document limitations and incomplete features.
- [ ] Prepare a working class demonstration.
- [ ] Verify submission requirements.

---

# OPTIONAL BACKLOG

## ALPHA-38: Support Conversational Corrections After Preview

**Type:** Feature  
**Priority:** P2  
**Area:** Backend, AI  
**Estimate:** 4 hours

### Acceptance Criteria

- [ ] Allow users to correct a previewed expense.
- [ ] Preserve previous conversation details.
- [ ] Recalculate shares after corrections.
- [ ] Validate the new allocation.
- [ ] Require confirmation again.
- [ ] Never save an outdated preview.

### Testing

Multi-turn correction tests with a mocked LLM.

---

## ALPHA-39: Add Itemized Manual Entry

**Type:** Feature  
**Priority:** P2  
**Area:** Frontend, Backend  
**Estimate:** 4 hours

### Acceptance Criteria

- [ ] Allow entry of multiple items.
- [ ] Allow item-specific participants.
- [ ] Support quantities.
- [ ] Support tax and tip.
- [ ] Reuse the Python allocation engine.
- [ ] Validate before saving.

### Testing

Test manual itemized calculations and invalid input.

---

## ALPHA-40: Add Settlement Placeholder

**Type:** Feature  
**Priority:** P2  
**Area:** Frontend  
**Estimate:** 2 hours

### Acceptance Criteria

- [ ] Display a Settle Up interface element.
- [ ] Clearly identify placeholder functionality.
- [ ] Do not initiate actual payments.
- [ ] Avoid changing balances without a recorded settlement.

### Testing

Verify placeholder rendering and that no real payment or balance mutation occurs.

---

# 5. Issue-to-Test Mapping

| Issue | Test File | Test Focus |
|---|---|---|
| ALPHA-01 | `test_setup.py` | Infrastructure |
| ALPHA-02 | `test_setup.py` | Documentation |
| ALPHA-03 | `test_setup.py` | Decision record |
| ALPHA-04 | `test_expense.py` | Pydantic schemas |
| ALPHA-05 | `test_expense.py` | Allocation |
| ALPHA-06 | `test_expense.py` | Rounding |
| ALPHA-07 | `test_validator.py` | Validation |
| ALPHA-08 | `test_backend.py` | SQLite |
| ALPHA-09 | `test_backend.py` | Sessions and API |
| ALPHA-10 | `test_llm.py` | Mock LLM |
| ALPHA-11 | `test_llm.py` | Claude wrapper |
| ALPHA-12 | `test_llm.py` | Parsing pipeline |

For issues #13–40, add tests inside the existing files where appropriate, or create feature-specific tests for frontend and end-to-end interactions.

The five-file structure applies specifically to the initial Python backend test suite. It does not restrict future test coverage.

---

# 6. Alpha Validation and Reporting

The Alpha evaluation uses six scenarios:

| Scenario | Difficulty | Capability |
|---|---|---|
| US-01 | Easy | Equal splits |
| US-02 | Easy | Selected participants |
| US-03 | Medium | Itemized splits |
| US-04 | Medium | Quantities and tax/tip |
| US-05 | Difficult | Missing information |
| US-06 | Difficult | Typos and unclear instructions |

### Scoring

A test attempt passes only when:

1. The correct payer is identified.
2. Every item and quantity is correct.
3. Every participant's share matches the expected answer to the cent.
4. The total is correct.
5. The validated preview is generated within five user prompts.

Accuracy is calculated as:

```text
Accuracy = (Successful Attempts / Total Attempts) × 100
```

For 18 attempts:

- 16/18 = 88.9% — Fail
- 17/18 = 94.4% — Pass
- 18/18 = 100% — Pass

### Evaluation Limitations

Internal Alpha testing provides initial evidence of functional reliability but does not establish performance across the broader target population.

The results must be reported accurately, including failures and unresolved cases.

---

# 7. Notes for Implementation

- The existing GitHub issues were originally planned for TypeScript, Fastify, Zod, and Vitest.
- The team has selected Python, FastAPI, Pydantic, SQLite, pytest, and React JavaScript instead.
- The architectural change does not alter the product's core acceptance criteria.
- Existing issue numbers, feature scope, and dependencies should remain consistent.
- The issue descriptions on GitHub should be updated to reflect the revised technology stack.
- `AGENTS.md` and other development documentation should be kept consistent with this plan.
- The application must use deterministic arithmetic and validation regardless of which LLM is selected.

**The primary Alpha goal remains demonstrating accurate conversational expense splitting through a validated, test-driven implementation.**