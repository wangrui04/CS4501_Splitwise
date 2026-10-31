
# Splitwise AI — Alpha Development User Stories

## Core Hypothesis

Our AI expense assistant can generate an accurate expense split within 5 user prompts in at least 90% of test attempts, across varying levels of complexity.

### Validation Criteria

- **Testers:** 3 development team members (internal Alpha)
- **Test scenarios:** 6 per tester
- **Total test attempts:** 18
- **Success threshold:** At least 17 out of 18 attempts must produce accurate expense splits within 5 user prompts.
- **Definition of accuracy:** Every participant's allocated amount must match the expected answer key.
- **Prompt counting:** Each user message counts as one prompt, including responses to clarification questions and corrections.
- **Safety guardrail:** No expense is saved until its allocation passes validation and the user confirms it.

---

# Level 1: Super Simple Splits

## User Story 1: Equal Expense Splitting

**ID:** US-01  
**Priority:** P0  
**Difficulty:** Simple  
**Labels:** `ai`, `backend`, `testing`

### User Story

As a user, I want to describe an expense that is shared equally among group members so that I can calculate everyone's share without doing the math manually.

### Acceptance Criteria

- [ ] The AI correctly identifies the payer, total amount, and participants.
- [ ] The expense is divided equally among the specified participants.
- [ ] Individual shares add up to the total amount.
- [ ] An accurate split is generated within 5 user prompts.
- [ ] The calculated breakdown is displayed before confirmation.

### Test Scenario

**Input:**

"I paid $30 for dinner for Sarah, Kayla, and Rui. Split it equally."

**Expected Result:**

| Person | Share |
|---|---:|
| Sarah | $10.00 |
| Kayla | $10.00 |
| Rui | $10.00 |
| **Total** | **$30.00** |

- Payer: Sarah
- Expected user prompts: 1

---

## User Story 2: Splitting an Expense Between Selected Members

**ID:** US-02  
**Priority:** P0  
**Difficulty:** Simple  
**Labels:** `ai`, `backend`, `testing`

### User Story

As a user, I want to specify which group members participated in an expense so that only those who benefited from it are charged.

### Acceptance Criteria

- [ ] The AI correctly identifies included and excluded participants.
- [ ] Group members who did not participate are allocated $0.
- [ ] The amount is split equally among included participants.
- [ ] The AI generates the correct allocation within 5 user prompts.
- [ ] The total allocated amount matches the expense total.

### Test Scenario

**Input:**

"I paid $24 for groceries, but only Kayla and Rui are sharing them."

**Expected Result:**

| Person | Share |
|---|---:|
| Sarah | $0.00 |
| Kayla | $12.00 |
| Rui | $12.00 |
| **Total** | **$24.00** |

- Payer: Sarah
- Expected user prompts: 1

---

# Level 2: More Complicated Multi-Way Splits

## User Story 3: Itemized Splitting With Different Participants

**ID:** US-03  
**Priority:** P0  
**Difficulty:** Moderate  
**Labels:** `ai`, `backend`, `testing`

### User Story

As a user, I want to describe multiple purchased items with different participants so that the AI can calculate each person's share based on what they actually consumed.

### Acceptance Criteria

- [ ] The AI identifies individual items and their prices.
- [ ] Each item is associated with the correct participants.
- [ ] Items shared by multiple people are divided correctly.
- [ ] Each person's share equals the sum of their allocated items.
- [ ] The AI generates an accurate split within 5 user prompts.
- [ ] An itemized breakdown is shown before saving.

### Test Scenario

**Input:**

"I paid $42. Kayla and I shared $12 nachos. Rui had a $15 burger, and Kayla had a $15 pasta."

**Expected Result:**

| Person | Items | Share |
|---|---|---:|
| Sarah | Half of nachos | $6.00 |
| Kayla | Half of nachos + pasta | $21.00 |
| Rui | Burger | $15.00 |
| **Total** | | **$42.00** |

- Payer: Sarah
- Expected user prompts: 1

---

## User Story 4: Unequal Quantities and Tax/Tip Allocation

**ID:** US-04  
**Priority:** P0  
**Difficulty:** Moderate  
**Labels:** `ai`, `backend`, `testing`

### User Story

As a user, I want the AI to account for different quantities purchased and additional charges such as tax and tip so that everyone pays an accurate share of the final bill.

### Acceptance Criteria

- [ ] The AI identifies quantities and individual item prices.
- [ ] The AI correctly calculates costs when participants purchase different quantities.
- [ ] Tax and tip are distributed according to the user's specified allocation method.
- [ ] If the tax/tip allocation method is unclear, the AI asks for clarification.
- [ ] The total of all allocated shares matches the final bill.
- [ ] An accurate split is generated within 5 user prompts.

### Test Scenario

**Input:**

"I paid for dinner. Kayla got two $10 drinks, Rui got one $10 drink, and I didn't have anything. The tip was $6. Split the tip proportionally."

**Expected Result:**

| Person | Items | Tip | Share |
|---|---|---:|---:|
| Sarah | Nothing | $0.00 | $0.00 |
| Kayla | Two drinks ($20) | $4.00 | $24.00 |
| Rui | One drink ($10) | $2.00 | $12.00 |
| **Total** | | **$6.00** | **$36.00** |

- Payer: Sarah
- Expected user prompts: 1

---

# Level 3: Worst-Case Scenarios

## User Story 5: Handling Missing and Ambiguous Information

**ID:** US-05  
**Priority:** P0  
**Difficulty:** Worst-case  
**Labels:** `ai`, `backend`, `testing`

### User Story

As a user, I want the AI assistant to recognize missing or ambiguous information and ask follow-up questions so that it can generate an accurate expense split without making incorrect assumptions.

### Acceptance Criteria

- [ ] The AI detects missing prices, payer information, or participants.
- [ ] The AI asks specific follow-up questions rather than inventing values.
- [ ] Information provided in previous prompts is retained.
- [ ] The AI handles obvious typos when the intended participant is unambiguous.
- [ ] Ambiguous names or descriptions trigger clarification.
- [ ] The AI generates an accurate split within 5 user prompts when the necessary information is supplied.
- [ ] An unresolved expense cannot be saved as a confirmed split.

### Test Scenario

**Prompt 1:**

"Me and Kayla shared nachoes, Rui got two drinks, and I paid."

**Expected AI Follow-Up:**

"How much were the nachos and each drink?"

**Prompt 2:**

"Nachos were $16 and drinks were $5 each. No tax or tip."

**Expected Result:**

| Person | Items | Share |
|---|---|---:|
| Sarah | Half of nachos | $8.00 |
| Kayla | Half of nachos | $8.00 |
| Rui | Two drinks | $10.00 |
| **Total** | | **$26.00** |

- Payer: Sarah
- Expected user prompts: 2
- Expected behavior: The AI retains the original participants and quantities after the clarification.

---

## User Story 6: Messy Language, Typos, and Unclear Instructions

**ID:** US-06  
**Priority:** P0  
**Difficulty:** Worst-case  
**Labels:** `ai`, `backend`, `testing`

### User Story

As a user, I want the AI assistant to understand spelling mistakes and clarify unclear instructions so that I can describe expenses naturally without needing to phrase everything perfectly.

### Acceptance Criteria

- [ ] The AI recognizes common spelling errors in item names and expense descriptions.
- [ ] The AI correctly interprets misspelled group member names when the intended person is unambiguous.
- [ ] The AI identifies unclear or contradictory splitting instructions.
- [ ] The AI asks clarification questions instead of making assumptions when the intended meaning is uncertain.
- [ ] The AI retains previously provided information after receiving clarification.
- [ ] The AI correctly allocates expenses based on the clarified instructions.
- [ ] The AI produces an accurate split within 5 user prompts.
- [ ] The final allocation is validated and displayed for user confirmation before saving.

### Test Scenario

**Prompt 1:**

"I paid for dinr. Me and Kayla shared nachoes for $16. Riu got 2 drnks for $5 each. Split the rest evenly."

**Expected AI Behavior:**

- Recognizes "dinr" as "dinner".
- Recognizes "nachoes" as "nachos".
- Recognizes "Riu" as "Rui".
- Recognizes "drnks" as "drinks".
- Identifies that "split the rest evenly" is unclear because no additional amount has been specified.
- Asks for clarification instead of assuming what "the rest" refers to.

**Expected AI Follow-Up:**

"I understand that Sarah and Kayla shared $16 nachos, and Rui had two $5 drinks. When you say 'split the rest evenly,' is there another charge to split?"

**Prompt 2:**

"No, that's everything. No tax or tip."

**Expected Result:**

| Person | Items | Share |
|---|---|---:|
| Sarah | Half of nachos | $8.00 |
| Kayla | Half of nachos | $8.00 |
| Rui | Two drinks | $10.00 |
| **Total** | | **$26.00** |

- Payer: Sarah
- Expected user prompts: 2
- Expected behavior: The AI interprets spelling mistakes correctly, clarifies ambiguous instructions, and generates the correct split.

---

# Supporting Application Features

## User Story 7: Manual Expense Entry

**ID:** US-07  
**Priority:** P0  
**Difficulty:** Core UI  
**Labels:** `frontend`, `backend`, `testing`

### User Story

As a user, I want to enter an expense manually so that I can record a bill without using the AI assistant.

### Acceptance Criteria

- [ ] The user selects a group, description, payer, amount, and participants.
- [ ] The application calculates each participant's share in integer cents.
- [ ] The breakdown is previewed before confirmation.
- [ ] Invalid totals, unknown members, and missing fields are rejected.
- [ ] Only a confirmed, validated expense is saved to the selected group.

### Test Scenario

Sarah enters a $30.00 dinner for Apartment 4B, paid by Sarah and shared equally by Sarah, Kayla, and Rui.

**Expected Result:**

| Person | Share |
|---|---:|
| Sarah | $10.00 |
| Kayla | $10.00 |
| Rui | $10.00 |
| **Total** | **$30.00** |

The expense appears in the group's history only after confirmation.

---

## User Story 8: Name-Based Sign-In

**ID:** US-08  
**Priority:** P0  
**Difficulty:** Core UI  
**Labels:** `frontend`, `backend`, `testing`

### User Story

As a user in the Alpha demo, I want to choose my name from a predefined roster so that the application can identify which groups and expenses belong to me.

### Acceptance Criteria

- [ ] The user can choose a valid demo name from the available group-member roster.
- [ ] An unknown name is rejected.
- [ ] A signed session identifies the current user on subsequent requests.
- [ ] Protected group routes reject requests without a valid session.
- [ ] The user can log out, invalidating the session.

### Test Scenario

Sarah selects her name and signs in.

**Expected Behavior:**

- Sarah can access her associated demo groups.
- Unknown names are rejected.
- Requests without a valid session receive `401 Unauthorized`.
- After logging out, Sarah can no longer access protected group endpoints.

**Scope Note:** Selecting a name is intended only for internal Alpha testing and is not production-grade authentication.

---

## User Story 9: Group Balances and Expense History

**ID:** US-09  
**Priority:** P0  
**Difficulty:** Core UI  
**Labels:** `frontend`, `backend`, `testing`

### User Story

As a group member, I want to see the expenses and running balances within my group so that I know who paid and how the costs were allocated.

### Acceptance Criteria

- [ ] The user can see groups associated with the current demo session.
- [ ] Each group's expenses display the description, payer, total, and participants' shares.
- [ ] The expense history is derived from saved, confirmed expenses.
- [ ] Running balances use saved allocations and payer amounts.
- [ ] The displayed balances are consistent with underlying expense records.

### Test Scenario

Sarah pays $30.00 for an equally shared dinner in Apartment 4B.

**Expected Result:**

- Sarah paid $30.00.
- Sarah's share is $10.00.
- Kayla's share is $10.00.
- Rui's share is $10.00.
- The group balances reflect that Kayla and Rui each owe Sarah $10.00 for this expense.

---

# User Story Summary

| ID | User Story | Difficulty | Core Capability |
|---|---|---|---|
| US-01 | Equal Expense Splitting | Simple | Basic natural-language interpretation |
| US-02 | Selected Member Splitting | Simple | Participant inclusion and exclusion |
| US-03 | Itemized Multi-Way Splitting | Moderate | Item-to-participant mapping |
| US-04 | Unequal Quantities and Tax/Tip | Moderate | Complex allocation rules |
| US-05 | Missing and Ambiguous Information | Worst-case | Clarification and context retention |
| US-06 | Messy Language, Typos, and Unclear Instructions | Worst-case | Typo handling and ambiguity clarification |
| US-07 | Manual Expense Entry | Core UI | Manual input, validation, and confirmation |
| US-08 | Name-Based Sign-In | Core UI | Demo user sessions and protected routes |
| US-09 | Group Balances and Expense History | Core UI | Saved expenses and per-person balances |

---

# Alpha Validation Plan

## Objective

Evaluate whether the AI expense assistant can generate accurate shared-expense allocations within 5 user prompts at least 90% of the time.

The six primary AI test scenarios correspond to US-01 through US-06. US-07 through US-09 are supporting application features with separate functional tests.

## Participants

For Alpha Development, the proposed testing scope involves 3 internal team members rather than recruiting 10 external users.

- **Internal testers:** 3 development team members
- **Test scenarios:** 6 per tester
- **Total attempts:** 18

External user testing may be conducted during a later development stage, depending on the professor's guidance.

## Testing Procedure

1. Prepare six expense-splitting scenarios and their expected answer keys.
2. Each team member independently completes all six scenarios using the AI assistant.
3. Record each user prompt, including clarification responses and corrections.
4. Compare the AI-generated allocations against the predefined answer keys.
5. Verify the payer, participants, quantities, total, and individual shares.
6. Record the number of prompts required to produce a correct split.
7. Mark an attempt successful only when the entire allocation is accurate within 5 prompts.
8. Verify that expenses cannot be saved without validation and explicit confirmation.

## Metrics

### Primary Metric: Split Accuracy Within 5 Prompts

Accuracy = (Successful attempts / Total attempts) × 100%

A successful attempt must:

- Produce the correct payer.
- Correctly identify purchased items and participants.
- Calculate every participant's share accurately.
- Match the expected total.
- Complete within 5 user prompts.

### Secondary Metrics

- Number of user prompts required.
- Number of clarification questions.
- Number of corrections.
- Error types (participants, quantities, amounts, tax/tip).
- Accuracy by difficulty level.

## Success Threshold

With 3 testers completing 6 scenarios each:

- Total attempts: 18
- Target accuracy: 90%
- Minimum successful attempts: 17
- Actual threshold reached with 17 passes: 94.4%

The hypothesis meets the predefined accuracy threshold if at least 17 out of 18 attempts produce completely correct splits within 5 user prompts.

## Limitations

- Testing involves only 3 internal team members.
- Team members already understand the application's intended behavior.
- Repeated scenarios may not represent the variety of real-world expenses.
- Results may vary depending on the LLM and wording of user inputs.
- Mocked LLM tests do not count as live AI validation attempts.
- Findings provide preliminary functional evidence rather than independent user validation.

---

# Test-Driven Development (TDD)

For each GitHub Issue:

1. Write automated tests based on the acceptance criteria.
2. Run tests and verify that they initially fail.
3. Implement the minimum functionality needed to pass the tests.
4. Rerun the tests and verify that they pass.
5. Refactor the implementation while keeping tests green.
6. Commit the tests and implementation to GitHub.

## General Edge Cases

- Expense totals that do not divide evenly into cents.
- Invalid or negative amounts.
- Unknown participants.
- Missing payer information.
- Missing item prices.
- Duplicate or ambiguous participant names.
- Multiple quantities of the same item.
- Excluded group members.
- Inconsistent expense totals.
- Conversational corrections that change previous allocations.
- Unresolved descriptions after 5 user prompts.

## Validation Guardrail

All generated allocations must pass deterministic validation before being shown as ready for confirmation.

The AI interprets natural-language descriptions and produces structured expense data. Regular application code performs the arithmetic.

No expense is permanently saved until the user reviews and confirms the final allocation.
