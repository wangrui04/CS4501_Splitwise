<issue_fields>Acceptance criteria, Testing, Required features</issue_fields>

# AGENTS.md

Guidance for AI coding agents working in this repository. Read this before generating code, docs, issues, or PRs.

> Note: the repository is named `CS4501_TonePerfect` for historical reasons. The selected project is **Splitwise with a Conversational Expense Assistant**. Do not build TonePerfect features.

## Project summary

A CS 4501 final project that recreates Splitwise's core shared-expense tracking (groups, expenses, who owes whom) and adds an AI assistant that lets users describe complicated splits in natural language, e.g.:

> "Anna and I shared the nachos, and everyone but Aly got a margarita."

The assistant extracts the payer, items, amounts, participants, exceptions, and unequal portions; asks about anything missing or ambiguous; and shows an itemized preview the user must confirm before balances change.

Core flow:

```text
Describe Expense → Identify Items and Participants → Ask for Missing Information
→ Calculate Each Person's Share → Validate the Allocation → Show Itemized Preview
→ User Confirms → Save Expense and Update Balances
```

Users can also make conversational corrections ("Actually, Anna had two margaritas"), which produce a revised preview before saving.

The full product spec is in [README-startupSelected.md](README-startupSelected.md). Alternative ideas in [ideas/](ideas/) are reference only — do not build features from them.

## MVP scope

Build within these limits unless an issue explicitly expands them:

- Small groups of friends or roommates.
- One currency per group.
- One payer per expense.
- Equal and custom item-level splits.
- Text-based expense descriptions (voice input comes later, only after the text workflow works reliably).
- Explicit tax and tip allocation rules.

MVP features: group creation and member management, manual expense entry, AI-generated expense drafts, follow-up questions, conversational corrections, share and balance calculation, validation, automatic retry, an itemized review/confirmation screen, expense history and individual balances, and recording settlements.

**Out of scope:** real payments or money transfers, bank connections, receipt scanning, multiple payers per expense, and multi-currency groups.

## Planned stack

| Layer | Choice |
| --- | --- |
| Frontend | React |
| Backend | Python (REST API) |
| Database | Groups, members, expenses, items, shares, balances, settlements |
| AI | LLM API with structured JSON output |
| Math | Regular application code (never the LLM) |
| Voice (later) | Speech-to-text API |

If you introduce a framework, library, or service not listed here, say so explicitly in the PR description and explain why.

Suggested layout once code exists:

```text
frontend/   React app
backend/    Python API, models, split calculation, LLM + validation pipeline
docs/       Design notes, API contracts
ideas/      Original startup pitches (do not modify)
```

## Architecture rules (non-negotiable)

These come from the product design and keep wrong allocations from silently changing balances.

1. **The LLM interprets; deterministic code calculates.** The LLM only turns natural language into structured expense data. All arithmetic (shares, tax/tip distribution, rounding, balances) happens in regular, unit-tested code. Never ask the LLM to compute amounts that get saved.

2. **Structured LLM output only.** The LLM returns JSON matching a defined schema, for example:

   ```json
   {
     "payer": "Sarah",
     "currency": "USD",
     "items": [
       {
         "description": "Nachos",
         "amount_cents": 2000,
         "participants": ["Sarah", "Anna"],
         "split_method": "equal"
       }
     ],
     "tax_and_tip_included": true,
     "missing_fields": []
   }
   ```

   Do not parse free-form prose. Resolve "I" / "me" to the signed-in user.

3. **Money is integer cents.** Store and calculate amounts as integers in the smallest currency unit (`amount_cents`). Never use floats for money. Rounding must be deterministic, and shares must sum exactly to the total; distribute leftover cents with a documented, consistent rule.

4. **Validation guardrail — nothing AI-generated is saved without validation and user confirmation.** Validators must check that:
   - The response follows the required schema.
   - Every payer and participant belongs to the selected group.
   - Required amounts, currency, and payer are present.
   - Item amounts and quantities are valid (positive, well-formed).
   - Split rules are supported and internally consistent.
   - Tax and tip handling is specified.
   - Calculated shares add up to the confirmed expense total.
   - Rounding does not create or lose money.
   - Unresolved ambiguity (e.g. two members named "Alex", an unknown name like "Allie") triggers a follow-up question instead of a guess.

5. **Self-correction loop.** When validation fails, send the specific validation error (and the valid member list when relevant) back to the LLM to revise the structure or ask a follow-up question. Cap automatic retries; when the cap is hit, ask the user to clarify or fall back to manual editing. Never show an invalid preview.

6. **Confirmation gates writes.** Balances update only after the user approves the itemized preview. Draft or pending expenses must not affect balances.

7. **Manual entry must always work** without the AI, and it uses the same calculation and validation code.

8. Keep retry limits, model names, prompts, and schemas in config/constants, not scattered inline.

## Coding conventions

**General**
- Small, focused functions and modules; one responsibility per file where practical.
- Descriptive names; no single-letter names outside short loops.
- Never commit secrets. API keys go in environment variables (`.env`, gitignored) with a checked-in `.env.example`.
- Never commit real user data. Use synthetic groups and expenses for fixtures.

**Python (backend)**
- Python 3.11+, PEP 8, type hints on all public functions.
- Format with `black`, lint with `ruff`.
- Use Pydantic models for the LLM output schema and API request/response bodies.
- Tests with `pytest`.

**React (frontend)**
- Functional components and hooks only.
- Format with Prettier, lint with ESLint.
- Format money for display only at the UI edge (cents → `$12.34`).
- The preview screen must make it clear who owes what per item before the user confirms.

## Testing

- Split calculation and rounding code needs thorough unit tests: equal splits, custom/unequal portions, quantities ("Anna had two"), exclusions ("everyone but Aly"), tax and tip distribution, and remainder-cent cases. Shares must always sum to the total.
- Every validator needs tests for both pass and fail cases (e.g. a non-member participant, ambiguous names, missing amounts, missing tax/tip rule).
- Test the self-correction loop with a mocked LLM: invalid output → retry → valid output, and retry cap → clarification/manual fallback.
- Test that unconfirmed drafts never change balances.
- Mock all external APIs (LLM, speech-to-text) in automated tests; do not call paid APIs in CI.
- New features must include tests; bug fixes should include a test that reproduces the bug.

## Git, issues, and PRs

- Branch off `main` with descriptive names: `feature/<short-name>`, `fix/<short-name>`, `docs/<short-name>`.
- Commit messages: imperative mood, concise summary line (e.g. `Add remainder-cent distribution to split calculator`).
- Keep PRs small and scoped to one issue; link the issue in the PR description.
- Don't modify files in [ideas/](ideas/) or the license.

**Issue format** — every GitHub issue must include these sections (per the `issue_fields` tag at the top of this file):

```markdown
## Required features
- What must be built or changed.

## Acceptance criteria
- [ ] Concrete, checkable conditions for "done".

## Testing
- How the change will be verified (unit tests, manual steps, test data).
```

## Documentation and formatting

- Markdown files use `#` headings, `---` section dividers where they help, and fenced code blocks with a language tag (`json`, `text`, `python`, etc.).
- Update the relevant README or `docs/` file whenever behavior, setup steps, or APIs change.
