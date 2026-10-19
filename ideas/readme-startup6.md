Startup Idea: Splitwise with a Conversational Expense Assistant
Overview
Splitwise is an application for tracking shared expenses and who owes whom.

Our project recreates its core expense-tracking functionality and adds an AI assistant that lets users describe complicated splits through text or voice.

For example:
“Anna and I shared the nachos, and everyone but Aly got a margarita.”

The system identifies:
- Who paid.
- Which items were purchased.
- How much each item cost.
- Who shared each item.
- Exceptions and unequal portions.
- Missing information that requires clarification.
It then generates an itemized preview for users to confirm before updating balances.
1. Solves One Problem Extremely Well
The startup focuses specifically on:

Helping groups divide shared expenses accurately without manually calculating each person’s share.

Users explain who shared what instead of converting a complicated situation into percentages or custom amounts themselves.

The application tracks expenses and balances. Actual payment processing is outside the MVP.
2. We Know the Target Customers or Have Direct Access to Them
Target users include:
- College roommates.
- Friends splitting restaurant bills.
- Students traveling together.
- Groups sharing groceries or household purchases.
- Clubs organizing shared purchases.
University campuses provide direct access to people who regularly share expenses.

We can test the application with classmates, roommates, and student organizations using realistic expense-splitting scenarios.
3. We Are Familiar With or Can Quickly Learn the Required Infrastructure
The MVP could use:
- React frontend.
- Python backend.
- Database for groups, members, expenses, and balances.
- LLM API.
- Structured JSON output for expense details.
- Regular application code for arithmetic and balance calculations.
- Speech-to-text API for optional voice input.
We would first build a text-based workflow, then add voice input after the core functionality works.

This keeps the infrastructure realistic for a small team to build.
4. Reimagines the Problem Space
Manual expense entry requires users to select participants and calculate custom allocations for complicated splits.

Our application instead lets users explain the expense as they would to a friend.

The application follows:
Describe Expense
  ↓
Identify Items and Participants
  ↓
Ask for Missing Information
  ↓
Calculate Each Person’s Share
  ↓
Validate the Allocation
  ↓
Show Itemized Preview
  ↓
User Confirms
  ↓
Save Expense and Update Balances

Users can also make conversational corrections:
“Actually, Anna had two margaritas.”

The assistant updates the proposed allocation and shows a revised preview before saving.
5. An LLM / Generative Model Is Core to the Solution
The LLM converts natural-language descriptions into structured expense information.

It interprets references such as:
- “Anna and I.”
- “Everyone except Aly.”
- “Just the roommates.”
- “Anna had two, and I had one.”
For example:
“I paid $20 total, including tax and tip, for nachos that Anna and I shared.”

If the signed-in user is Sarah, the LLM could produce:
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

If information is missing, the assistant asks questions such as:
- “How much were the nachos and each margarita?”
- “Who paid?”
- “Does that amount include tax and tip?”
- “How should tax and tip be divided?”
Regular application code calculates the final shares.

The LLM therefore provides the conversational understanding, while deterministic code handles the arithmetic.
6. Validation Guardrail
No AI-generated expense allocation is saved before validation and user confirmation.

Validators check:
- The structured response follows the required schema.
- Every payer and participant belongs to the selected group.
- Required amounts, currency, and payer information are present.
- Item amounts and quantities are valid.
- Split rules are supported and internally consistent.
- Tax and tip handling has been specified.
- Calculated shares add up to the confirmed expense total.
- Rounding does not create or lose money.
- Unresolved ambiguity triggers a follow-up question.
For example, the assistant must ask who “Alex” refers to if multiple group members have that name.

This prevents invalid allocations from silently changing balances.

Users also review the interpretation because correct arithmetic does not necessarily mean the assistant understood their description correctly.
7. Self-Correction Loop
If the generated expense structure fails validation, the validator sends the specific problem back to the LLM.

Example:
Validation Error:

The participant "Allie" is not in this group.
Valid members are Sarah, Anna, Aly, and Ben.

Recheck the original description and use an existing
member only if the reference is unambiguous.
Otherwise, ask the user to clarify.

The LLM revises the structure or asks a follow-up question when information is missing.

The application recalculates and validates the revised allocation.

Automatic retries are limited. If validation still fails, the assistant requests clarification or lets the user edit the expense manually.

Only a validated preview reaches the confirmation step.

Balances update only after the user approves the expense.
8. Deployability
A first version could focus only on:
- Small groups of friends or roommates.
- One currency per group.
- One payer per expense.
- Equal and custom item-level splits.
- Text-based expense descriptions.
- Explicit tax and tip allocation rules.
The deployed system could include:
- Group creation and member management.
- Manual expense entry.
- AI-generated expense drafts.
- Follow-up questions for missing information.
- Conversational corrections.
- Share and balance calculations.
- Validation.
- Automatic retry.
- An itemized review and confirmation screen.
- Expense history and individual balances.
- Recording settlements without transferring money.
Voice input could be added once the text workflow works reliably.

No bank connections, actual payments, or receipt scanning are required.

This represents a realistic and fully deployable MVP.
