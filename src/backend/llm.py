
from __future__ import annotations

from pydantic import ValidationError
from backend.schemas import ParsedExpense


class LlmError(Exception):
    pass


class FakeLlmClient:
    def __init__(self, scripted):
        self.scripted = list(scripted)
        self.calls = []

    def parse(self, *, messages, roster, current_user):
        self.calls.append({
            "messages": [dict(message) for message in messages],
            "roster": list(roster),
            "current_user": current_user,
        })

        if not self.scripted:
            raise LlmError("Scripted LLM exhausted")

        return self.scripted.pop(0)


class ClaudeLlmClient:
    def __init__(
        self,
        api_key,
        model="claude-sonnet-5-5",
        sdk=None,
    ):
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set"
            )

        self.model = model

        if sdk is None:
            from anthropic import Anthropic

            sdk = Anthropic(
                api_key=api_key,
                timeout=20.0,
                max_retries=0,
            )

        self.sdk = sdk

    def parse(self, *, messages, roster, current_user):
        system_prompt = (
            "Extract structured expense data. "
            "Never calculate shares or totals. "
            "Never invent amounts, payer, tax, or tip. "
            "Represent I/me as ME. "
            "Use all_except for everyone except a member. "
            "Ask about unknown details using openQuestions. "
            "Correct name typos only when unambiguous. "
            "Ask about ambiguous participant references. "
            f"Group roster: {roster}. "
            f"Signed-in user: {current_user}."
        )

        last_error = None

        for attempt in range(2):
            try:
                request_messages = [
                    dict(message)
                    for message in messages
                ]

                if attempt and last_error is not None:
                    request_messages.append({
                        "role": "user",
                        "content": (
                            "Previous tool response invalid: "
                            f"{last_error}. "
                            "Return a corrected structured tool call."
                        ),
                    })

                response = self.sdk.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    temperature=0,
                    system=system_prompt,
                    messages=request_messages,
                    tools=[{
                        "name": "parse_expense",
                        "description": (
                            "Extract expense details only"
                        ),
                        "input_schema": (
                            ParsedExpense.model_json_schema()
                        ),
                    }],
                    tool_choice={
                        "type": "tool",
                        "name": "parse_expense",
                    },
                )

                blocks = [
                    block
                    for block in response.content
                    if (
                        getattr(block, "type", None)
                        == "tool_use"
                        and getattr(block, "name", None)
                        == "parse_expense"
                    )
                ]

                if not blocks:
                    raise LlmError(
                        "LLM_INVALID_OUTPUT: "
                        "missing structured tool call"
                    )

                parsed = ParsedExpense.model_validate(
                    blocks[0].input
                )

                return parsed.model_dump()

            except (ValidationError, LlmError) as exc:
                last_error = str(exc)

            except (ConnectionError, TimeoutError):
                last_error = "Temporary network failure"

            except Exception as exc:
                # Anthropic SDK uses dedicated error types.
                if exc.__class__.__name__ in (
                    "APIConnectionError",
                    "APITimeoutError",
                ):
                    last_error = "Temporary network failure"
                else:
                    raise LlmError(
                        "LLM_REQUEST_FAILED"
                    ) from None

        raise LlmError(
            "LLM_INVALID_OUTPUT: " + str(last_error)
        )
