
# Alpha Hypothesis and Testing Plan

## Core Hypothesis

Our AI expense assistant can generate an accurate expense
split within 5 user prompts in at least 90% of test attempts,
across varying levels of complexity.

## Alpha Testing Scope

- Testers: 3 development team members
- Scenarios: 6
- Attempts: Each team member tests all 6 scenarios
- Total test attempts: 18
- Target accuracy: >= 90%
- Minimum passing attempts: 17 out of 18

## Test Categories

### Simple Splits
1. Equal expense splitting
2. Splitting among selected participants

### Complicated Multi-Way Splits
3. Multiple items with different participants
4. Unequal quantities and tax/tip allocation

### Worst-Case Scenarios
5. Missing information, ambiguity, and typos
6. Conversational corrections

## Success Criteria

A test attempt passes if:
- The AI correctly identifies the payer.
- All items and their amounts are correctly interpreted.
- Each participant receives the correct allocation.
- The total allocation matches the expense total.
- The correct split is produced within 5 user prompts.

A prompt is defined as one user message sent to the LLM,
including clarification responses and corrections.

## Evaluation Method

1. Prepare the expected answer for each scenario.
2. Each team member independently tests all 6 scenarios.
3. Record the AI's generated split.
4. Compare the results against the expected answer.
5. Record the number of prompts used.
6. Mark each attempt as Pass or Fail.
7. Calculate overall accuracy.

Accuracy = (Passed Attempts / Total Attempts) * 100

## Limitations

This is internal Alpha testing conducted by the development
team rather than independent users.

The results evaluate initial functional reliability but
do not establish accuracy across the broader target population.

Further external user validation will be needed.
