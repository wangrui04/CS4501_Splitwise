# MVP Issues — Due Oct 22 (before class)

Issues for the MVP demo and presentation. Each issue below is ready to paste into GitHub: use the `###` line as the title and everything under it as the body.

**MVP approach:** a thin, working vertical slice of the AI flow (describe expense → follow-up question → validated itemized preview → confirm → balances) running on a seeded demo group. No auth, no real database, no voice, no payments. A recorded demo video is the backup if anything breaks.

**Priority key:** `P0` = required for the demo/presentation · `P1` = makes the demo stronger · `P2` = stretch, cut first.

**Labels used:** `setup`, `backend`, `frontend`, `ai`, `testing`, `presentation`

| # | Title | Priority | Labels |
| --- | --- | --- | --- |
| 1 | Project scaffold (React + Python API) | P0 | setup |
| 2 | Seeded demo group and in-memory data store | P0 | backend |
| 3 | Deterministic split calculator (integer cents) | P0 | backend, testing |
| 4 | Balance calculation (who owes whom) | P0 | backend, testing |
| 5 | LLM expense parser with structured JSON output | P0 | ai, backend |
| 6 | Expense allocation validators | P0 | ai, backend, testing |
| 7 | Self-correction loop and follow-up questions | P0 | ai, backend |
| 8 | Expense draft / confirm API endpoints | P0 | backend |
| 9 | Chat input and itemized preview screen | P0 | frontend |
| 10 | Balances and expense history screen | P1 | frontend |
| 11 | Conversational corrections | P1 | ai, backend, frontend |
| 12 | Manual expense entry | P2 | frontend, backend |
| 13 | Demo script, scenarios, and backup video | P0 | presentation |
| 14 | Slides: problem and market | P0 | presentation |
| 15 | Slides: value proposition, hypothesis, and scope | P0 | presentation |
| 16 | Slides: validation plan and success metrics | P0 | presentation |
| 17 | Assemble deck, submit PDF, and rehearse | P0 | presentation |

Suggested order: start #1–#4 and #14–#16 in parallel on day 1; #5–#9 on day 1–2; #13 and #17 on day 2.

---

### 1. Project scaffold (React + Python API)

**Priority:** P0 · **Labels:** `setup` · **Estimate:** 1–2 h · **Depends on:** none

**Summary**
Set up the repo so everyone can run the frontend and backend locally with one command each.

## Required features
- `frontend/`: React app (Vite) with a placeholder home page.
- `backend/`: Python API (FastAPI) with a `GET /health` endpoint.
- Frontend can call the backend (CORS or dev proxy configured).
- `.env.example` with the LLM API key variable; `.env` in `.gitignore`.
- README section: how to install and run both apps.
- `black` + `ruff` (backend) and Prettier + ESLint (frontend) configured.

## Acceptance criteria
- [ ] A teammate can clone the repo, follow the README, and see the frontend display a response from `/health`.
- [ ] No secrets are committed.
- [ ] Linters run without errors on the scaffold.

## Testing
- One `pytest` test for `/health`.
- Manual: fresh clone on a second teammate's machine.

**Out of scope:** deployment, CI, auth.

---

### 2. Seeded demo group and in-memory data store

**Priority:** P0 · **Labels:** `backend` · **Estimate:** 2 h · **Depends on:** #1

**Summary**
Provide the data the demo needs without building auth or a real database.

## Required features
- Pydantic models: `Group`, `Member`, `Expense`, `ExpenseItem`, `Share`, and an expense status of `draft` or `confirmed`.
- In-memory store (or a single SQLite file) seeded with one demo group: Sarah, Anna, Aly, Ben.
- Signed-in user hardcoded to Sarah (config constant).
- All amounts stored as integer cents (`amount_cents`), one currency per group (USD).

## Acceptance criteria
- [ ] Backend starts with the demo group already loaded.
- [ ] There is a way to reset the store to the seed state (endpoint or restart) so the demo can be repeated.
- [ ] No float money values anywhere in the models.

## Testing
- Unit test that the seed loads 4 members and zero expenses.

**Out of scope:** user accounts, creating groups, persistence across restarts (unless SQLite is trivial).

---

### 3. Deterministic split calculator (integer cents)

**Priority:** P0 · **Labels:** `backend`, `testing` · **Estimate:** 3 h · **Depends on:** #2

**Summary**
Pure functions that turn a structured expense (items, participants, quantities, tax/tip rule) into per-person shares. This is the only place amounts are calculated — the LLM never does math.

## Required features
- Equal split of an item among its participants.
- Quantity-based split (e.g. "Anna had two margaritas, I had one").
- Tax and tip: either already included in item amounts, or a separate amount distributed proportionally to each person's subtotal.
- Remainder cents distributed with a fixed, documented rule (e.g. one extra cent each in group member order).
- Returns per-person totals and a per-item breakdown for the preview.

## Acceptance criteria
- [ ] Shares always sum exactly to the expense total (no created or lost cents).
- [ ] Same input always produces the same output.
- [ ] Unsupported split methods raise a clear error instead of guessing.

## Testing
- `pytest` cases: equal split, $10.00 split three ways (remainder cent), quantities, exclusions ("everyone but Aly"), proportional tax/tip, single-person item.
- Property-style check: for many random inputs, the sum of shares equals the total.

---

### 4. Balance calculation (who owes whom)

**Priority:** P0 · **Labels:** `backend`, `testing` · **Estimate:** 2 h · **Depends on:** #3

**Summary**
Compute each member's net balance from confirmed expenses only.

## Required features
- Net balance per member (positive = is owed, negative = owes).
- Simple "X owes Y $Z" list derived from net balances.
- Only `confirmed` expenses count; drafts are ignored.

## Acceptance criteria
- [ ] Net balances across the group always sum to zero.
- [ ] Creating a draft does not change any balance.

## Testing
- `pytest`: one expense, multiple expenses, draft ignored, zero-sum check.

**Out of scope:** recording settlements (can be added later), debt simplification beyond the basic list.

---

### 5. LLM expense parser with structured JSON output

**Priority:** P0 · **Labels:** `ai`, `backend` · **Estimate:** 3–4 h · **Depends on:** #2

**Summary**
Convert a natural-language description into the structured expense schema from the spec.

## Required features
- Pydantic schema matching the spec: `payer`, `currency`, `items[]` (`description`, `amount_cents`, `quantity` per participant if needed, `participants`, `split_method`), `tax_and_tip_included`, `missing_fields`, and an optional `clarifying_question`.
- Prompt includes the group member list and the signed-in user so "I"/"me" resolves to Sarah and "everyone except Aly" resolves to real members.
- LLM is told to list missing information in `missing_fields` rather than invent amounts or people.
- Model name, prompt, and schema live in config/constants; API key from `.env`.

## Acceptance criteria
- [ ] "I paid $20 total, including tax and tip, for nachos that Anna and I shared." produces the spec's example JSON.
- [ ] "Anna and I shared the nachos, and everyone but Aly got a margarita." (no prices) returns `missing_fields` that include the prices.
- [ ] Output that isn't valid against the schema is rejected (it goes to #7, not the user).

## Testing
- Unit tests with a mocked LLM client (no paid API calls in tests).
- Manual: run the 5 demo scenarios from #13 against the real API and record the results.

---

### 6. Expense allocation validators

**Priority:** P0 · **Labels:** `ai`, `backend`, `testing` · **Estimate:** 3 h · **Depends on:** #3, #5

**Summary**
The guardrail between the LLM and the user. Each check returns a specific, human-readable error message that can be fed back to the LLM.

## Required features
Validators that check:
- Schema is valid.
- Payer and every participant are members of the group.
- Amounts, currency, and payer are present.
- Amounts and quantities are positive and well-formed.
- Split method is supported and consistent with the item.
- Tax/tip handling is specified.
- Calculated shares (from #3) sum to the expense total.
- Ambiguous or unknown names (e.g. "Allie", or two members with the same name) are flagged so the system asks a question instead of guessing.

## Acceptance criteria
- [ ] Every validator has a clear error message, e.g. `The participant "Allie" is not in this group. Valid members are Sarah, Anna, Aly, and Ben.`
- [ ] A fully valid draft passes all checks.

## Testing
- `pytest`: one passing and at least one failing case per validator.

---

### 7. Self-correction loop and follow-up questions

**Priority:** P0 · **Labels:** `ai`, `backend` · **Estimate:** 2–3 h · **Depends on:** #5, #6

**Summary**
Orchestrate parse → validate → retry. Only validated drafts or clarifying questions reach the user.

## Required features
- On validation failure, send the original description, the previous output, and the specific errors back to the LLM.
- Retry cap in config (e.g. 2).
- If information is missing or ambiguous, return a follow-up question to the user (e.g. "How much was each margarita?").
- The user's answer is combined with the conversation so far and re-parsed.
- If the cap is hit, return a friendly "couldn't figure this out — please clarify" message. Never an invalid preview.

## Acceptance criteria
- [ ] An invalid first response that is fixed on retry produces a valid preview.
- [ ] Repeated failures stop at the cap and return a clarification request.
- [ ] Missing prices lead to a question, not invented numbers.

## Testing
- `pytest` with a mocked LLM: fail → pass; fail → fail → cap; missing field → question → answer → valid.

---

### 8. Expense draft / confirm API endpoints

**Priority:** P0 · **Labels:** `backend` · **Estimate:** 2 h · **Depends on:** #4, #7

**Summary**
The API the frontend uses for the full flow.

## Required features
- `POST /groups/{id}/expenses/draft`: takes a description and returns a validated draft (with an itemized per-person breakdown) or a follow-up question.
- `POST /drafts/{id}/reply`: takes the user's answer to a question (or a correction, see #11) and returns an updated draft or question.
- `POST /drafts/{id}/confirm`: saves the expense as `confirmed`.
- `GET /groups/{id}/balances` and `GET /groups/{id}/expenses`.
- `POST /reset` (demo only) to restore the seed data.

## Acceptance criteria
- [ ] Balances change only after `confirm`.
- [ ] Confirming an invalid or already-confirmed draft returns an error.

## Testing
- `pytest` API tests with a mocked LLM covering draft → question → reply → confirm → balances.

---

### 9. Chat input and itemized preview screen

**Priority:** P0 · **Labels:** `frontend` · **Estimate:** 4 h · **Depends on:** #8 (can start with mocked responses)

**Summary**
The main demo screen: describe an expense, answer any questions, review the itemized preview, then confirm.

## Required features
- Chat-style text input with the conversation history (user messages, assistant questions).
- Loading state while the assistant works.
- Itemized preview card: each item, its amount, who shared it, each person's share, tax/tip, totals, and who paid.
- "Confirm" and "Cancel" buttons. Confirm calls the API and shows success.
- Money displayed as `$12.34` (converted from cents only in the UI).
- Clean, presentable styling, since screenshots of this screen go in the slides.

## Acceptance criteria
- [ ] The full nachos/margaritas scenario can be completed in the UI from description to confirmation.
- [ ] Errors (API down, LLM failure) show a readable message instead of a blank screen.

## Testing
- Manual walkthrough of all demo scenarios from #13.
- Optional: one component test for the preview card.

---

### 10. Balances and expense history screen

**Priority:** P1 · **Labels:** `frontend` · **Estimate:** 2 h · **Depends on:** #8

**Summary**
Show the payoff after confirming: updated balances.

## Required features
- Group balance list ("Anna owes Sarah $14.50").
- List of confirmed expenses with expandable item breakdowns.
- Refreshes after an expense is confirmed.

## Acceptance criteria
- [ ] After confirming the demo expense, balances update on screen without a page reload.

## Testing
- Manual: confirm two expenses and check the balances against hand-calculated values.

---

### 11. Conversational corrections

**Priority:** P1 · **Labels:** `ai`, `backend`, `frontend` · **Estimate:** 2 h · **Depends on:** #7, #9

**Summary**
Let users fix a draft in plain language before confirming, e.g. "Actually, Anna had two margaritas."

## Required features
- When a draft preview is showing, a new message is treated as a correction to that draft.
- The corrected draft goes through validation (#6/#7) and recalculation (#3) again.
- The UI shows the revised preview, ideally highlighting what changed.

## Acceptance criteria
- [ ] "Actually, Anna had two margaritas" updates Anna's share and the totals correctly.
- [ ] The corrected draft is still validated before it is shown.

## Testing
- `pytest` with a mocked LLM for the correction path.
- Manual demo run.

---

### 12. Manual expense entry

**Priority:** P2 · **Labels:** `frontend`, `backend` · **Estimate:** 3 h · **Depends on:** #3, #8

**Summary**
A non-AI form (payer, items, amounts, participants) that uses the same calculator and validators. Useful as a side-by-side comparison in the demo or user tests, but cut it first if time is short.

## Required features
- Form to add items, amounts, and participants; choose the payer.
- Uses the same calculation and validation as the AI flow.

## Acceptance criteria
- [ ] A manually entered expense produces the same shares as the equivalent AI-parsed expense.

## Testing
- `pytest` comparing manual vs parsed input for the same scenario.

---

### 13. Demo script, scenarios, and backup video

**Priority:** P0 · **Labels:** `presentation` · **Estimate:** 2 h · **Depends on:** #9

**Summary**
A demo that fits about 60 seconds and works no matter which teammate presents.

## Required features
- 3–5 fixed demo scenarios with their expected results calculated by hand, e.g.:
  1. Simple: "I paid $20 including tax and tip for nachos Anna and I shared."
  2. Exclusion + follow-up: "Anna and I shared the nachos, and everyone but Aly got a margarita." → assistant asks for prices.
  3. Unknown name: "...Allie had a beer..." → assistant asks who Allie is.
  4. Correction: "Actually, Anna had two margaritas."
- Written step-by-step demo script, including what to say at each step.
- A 45–60 second screen recording of the full flow as a backup (and for the slides if the live demo isn't allowed).
- Screenshots of the chat, the preview, and balances for the slides.

## Acceptance criteria
- [ ] Every teammate has run the live demo at least once.
- [ ] Backup video is saved somewhere every teammate can open offline.

## Testing
- Run every scenario against the real LLM 3 times; note any inconsistent results and adjust the prompt or scenarios.

---

### 14. Slides: problem and market

**Priority:** P0 · **Labels:** `presentation` · **Estimate:** 2 h · **Depends on:** none

**Summary**
Section 1 of the deck (about 1.5 min): 2 slides.

## Required features
- **Pain point and target user:** complicated group splits (shared items, exclusions, unequal portions, tax/tip) force people to do mental math or enter custom amounts. Target: college roommates, friends at restaurants, students traveling, clubs.
- **Market and current solutions:** market relevance/size with cited sources (e.g. Splitwise, Venmo, and Tricount user numbers; the size of the US college population). Alternatives and their shortcomings: Splitwise (manual custom splits), Venmo (payments only, no itemization), receipt-scan apps (need a receipt, don't capture "who shared what"), spreadsheets/calculators.

## Acceptance criteria
- [ ] Every market number has a source in the speaker notes.
- [ ] Maximum one short sentence per bullet; uses a visual (comparison table or chart).

## Testing
- Timed read-through: the section fits in 1.5 minutes.

---

### 15. Slides: value proposition, hypothesis, and scope

**Priority:** P0 · **Labels:** `presentation` · **Estimate:** 2 h · **Depends on:** #13 (for screenshots)

**Summary**
Section 2 (about 2 min): 3 slides.

## Required features
- **Value proposition:** "Describe the expense like you'd tell a friend; we do the split." Show the flow diagram (Describe → Clarify → Calculate → Validate → Preview → Confirm).
- **Core hypothesis** (one sentence, testable). Draft: *Students splitting complicated group expenses will record them faster and at least as accurately by describing them in natural language than by entering custom splits manually, and will trust the AI's preview enough to confirm it.*
- **Scope and demo:** screenshots or video of the MVP, plus why these features: the AI parse + validation + confirmation is the riskiest assumption; auth, payments, voice, and receipt scanning were cut on purpose.

## Acceptance criteria
- [ ] The hypothesis directly matches the KPIs in #16.
- [ ] The demo slide is mostly visuals, not text.

## Testing
- Timed read-through: the section fits in 2 minutes, including the demo.

---

### 16. Slides: validation plan and success metrics

**Priority:** P0 · **Labels:** `presentation` · **Estimate:** 2 h · **Depends on:** #15

**Summary**
Section 3 (about 1.5 min): 2 slides. Numbers below are proposals for the team to agree on.

## Required features
- **Validation plan:**
  - Sample: about 20–30 students who regularly split expenses.
  - Channel: roommates, classmates, and 2–3 student organizations.
  - Method: moderated task-based test. Each participant records the same 3 scripted scenarios with the assistant and manually (in Splitwise or our form), in random order, then takes a short survey.
- **Success metrics and thresholds** (example):
  - Parse accuracy: ≥ 85% of scenarios produce a correct preview with at most 1 follow-up question.
  - Speed: median time to record an expense is ≥ 40% faster than manual entry.
  - Trust: ≥ 80% of correct previews are confirmed without manual edits.
  - Preference: ≥ 70% would choose the assistant over manual entry.
  - State what result disproves the hypothesis (e.g. accuracy < 70% or no speed gain).

## Acceptance criteria
- [ ] Every KPI has a specific number and maps back to the hypothesis.
- [ ] Sample size, channel, and method are all stated.

## Testing
- Timed read-through: the section fits in 1.5 minutes.

---

### 17. Assemble deck, submit PDF, and rehearse

**Priority:** P0 · **Labels:** `presentation` · **Estimate:** 3 h (team) · **Depends on:** #13–#16

**Summary**
Turn everything into one clean deck (title slide + about 8 content slides), submit it, and make sure anyone can present it.

## Required features
- Title slide: product name, one-line tagline, team member names.
- Consistent, clean template; diagrams and screenshots over text.
- Speaker notes on every slide.
- Export to PDF and submit on Canvas before class on Oct 22.
- Q&A prep doc with likely questions: Why not just use Splitwise? What if the AI gets it wrong? Cost per LLM call? Privacy? How will you get users?

## Acceptance criteria
- [ ] PDF submitted on Canvas before the deadline (confirm the submission shows up).
- [ ] Every team member has delivered the full talk in ≤ 5:00 at least once (presenter is chosen at random).
- [ ] The team has practiced answering the Q&A list.

## Testing
- Full timed run-through with a stopwatch; cut content until it consistently fits under 5 minutes.
