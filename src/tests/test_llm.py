
import copy
from unittest.mock import MagicMock
import pytest

from backend.schemas import ParsedExpense
from backend.llm import (
    FakeLlmClient,
    ClaudeLlmClient,
    LlmError,
)
from backend.pipeline import parse_turn


ROSTER = ["Sarah", "Kayla", "Rui"]


def expense(price="30.00", payer="Sarah"):
    return {
        "description": "Dinner",
        "payer": payer,
        "items": [{
            "name": "Pizza",
            "quantity": 1,
            "unitPrice": price,
            "participants": {
                "mode": "all",
                "names": [],
            },
        }],
        "charges": [],
        "statedTotal": price,
        "openQuestions": [],
    }


def user_message(content):
    return {"role": "user", "content": content}


def tool_response(data):
    block = MagicMock()
    block.type = "tool_use"
    block.name = "parse_expense"
    block.input = data

    response = MagicMock()
    response.content = [block]
    return response


def make_claude_client(responses):
    sdk = MagicMock()
    sdk.messages.create.side_effect = responses

    client = ClaudeLlmClient(
        api_key="fake-test-key",
        model="claude-sonnet-5-5",
        sdk=sdk,
    )

    return client, sdk


# Issue #10: Mock LLM

def test_fake_llm_returns_scripted_outputs():
    fake = FakeLlmClient([
        expense("30.00"),
        expense("45.00"),
    ])

    first = fake.parse(
        messages=[user_message("First bill")],
        roster=ROSTER,
        current_user="Sarah",
    )

    second = fake.parse(
        messages=[user_message("Second bill")],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert first == expense("30.00")
    assert second == expense("45.00")


def test_fake_llm_fails_when_exhausted():
    fake = FakeLlmClient([expense()])

    fake.parse(
        messages=[user_message("Dinner")],
        roster=ROSTER,
        current_user="Sarah",
    )

    with pytest.raises(LlmError):
        fake.parse(
            messages=[user_message("Another dinner")],
            roster=ROSTER,
            current_user="Sarah",
        )


@pytest.mark.parametrize("scenario", [
    expense("30.00"),
    expense("24.00"),
    expense("42.00"),
    {**expense(), "payer": None},
    {**expense(), "statedTotal": None},
    {
        **expense(),
        "openQuestions": [{
            "field": "payer",
            "question": "Who paid?",
        }],
    },
])
def test_six_scripted_scenarios_parse(scenario):
    result = ParsedExpense.model_validate(scenario)
    assert result is not None


def test_fake_llm_records_calls():
    fake = FakeLlmClient([expense()])

    fake.parse(
        messages=[user_message("Dinner")],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert len(fake.calls) == 1
    assert fake.calls[0]["current_user"] == "Sarah"


# Issue #11: Claude API wrapper

def test_claude_accepts_valid_structured_output():
    client, sdk = make_claude_client([
        tool_response(expense())
    ])

    result = client.parse(
        messages=[user_message("Split dinner")],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert result == expense()
    assert sdk.messages.create.call_count == 1


def test_claude_rejects_text_only_response():
    response = MagicMock()
    block = MagicMock()
    block.type = "text"
    block.text = "Everyone owes $10"
    response.content = [block]

    client, _ = make_claude_client([response])

    with pytest.raises(LlmError):
        client.parse(
            messages=[user_message("Split dinner")],
            roster=ROSTER,
            current_user="Sarah",
        )


def test_invalid_output_retries_once():
    invalid = {**expense(), "shares": [1000, 1000, 1000]}

    client, sdk = make_claude_client([
        tool_response(invalid),
        tool_response(expense()),
    ])

    result = client.parse(
        messages=[user_message("Split dinner")],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert result == expense()
    assert sdk.messages.create.call_count == 2


def test_invalid_output_stops_after_retry():
    invalid = {**expense(), "totalCents": 3000}

    client, sdk = make_claude_client([
        tool_response(invalid),
        tool_response(invalid),
    ])

    with pytest.raises(LlmError, match="LLM_INVALID_OUTPUT"):
        client.parse(
            messages=[user_message("Split dinner")],
            roster=ROSTER,
            current_user="Sarah",
        )

    assert sdk.messages.create.call_count == 2


def test_forced_tool_choice():
    client, sdk = make_claude_client([
        tool_response(expense())
    ])

    client.parse(
        messages=[user_message("Split dinner")],
        roster=ROSTER,
        current_user="Sarah",
    )

    kwargs = sdk.messages.create.call_args.kwargs

    assert kwargs["model"] == "claude-sonnet-5-5"
    assert kwargs["tool_choice"] == {
        "type": "tool",
        "name": "parse_expense",
    }


def test_api_key_not_logged(caplog):
    client, _ = make_claude_client([
        tool_response(expense())
    ])

    with caplog.at_level("DEBUG"):
        client.parse(
            messages=[user_message("Dinner")],
            roster=ROSTER,
            current_user="Sarah",
        )

    assert "fake-test-key" not in caplog.text


def test_network_error_retries_once():
    client, sdk = make_claude_client([
        ConnectionError("Temporary connection failure"),
        tool_response(expense()),
    ])

    result = client.parse(
        messages=[user_message("Dinner")],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert result == expense()
    assert sdk.messages.create.call_count == 2


# Issue #12: Natural-language parsing pipeline

def test_equal_split_pipeline():
    fake = FakeLlmClient([expense()])

    result = parse_turn(
        llm=fake,
        conversation=[
            user_message(
                "Sarah paid $30 for pizza for everyone"
            )
        ],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert result["type"] == "preview"

    preview = result["preview"]
    assert preview["totalCents"] == 3000
    assert preview["validated"] is True

    shares = {
        s["name"]: s["cents"]
        for s in preview["shares"]
    }

    assert shares == {
        "Sarah": 1000,
        "Kayla": 1000,
        "Rui": 1000,
    }


def test_pipeline_asks_for_missing_price():
    data = expense()
    data["items"][0]["unitPrice"] = None
    data["statedTotal"] = None

    fake = FakeLlmClient([data])

    result = parse_turn(
        llm=fake,
        conversation=[user_message("We shared pizza")],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert result["type"] == "question"
    assert "how much" in result["question"].lower()


def test_pipeline_asks_about_unknown_name():
    data = expense()
    data["items"][0]["participants"] = {
        "mode": "only",
        "names": ["Ben"],
    }

    fake = FakeLlmClient([data])

    result = parse_turn(
        llm=fake,
        conversation=[
            user_message("Ben and I shared dinner")
        ],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert result["type"] == "question"
    assert "Ben" in result["question"]


def test_me_resolves_to_current_user():
    data = expense("12.00", "ME")
    data["items"][0]["unitPrice"] = "12.00"
    data["items"][0]["participants"] = {
        "mode": "only",
        "names": ["ME"],
    }

    fake = FakeLlmClient([data])

    result = parse_turn(
        llm=fake,
        conversation=[
            user_message("I paid $12 for lunch")
        ],
        roster=ROSTER,
        current_user="Kayla",
    )

    assert result["type"] == "preview"
    assert result["preview"]["payer"] == "Kayla"


def test_pipeline_rejects_computed_llm_shares():
    invalid = {
        **expense(),
        "shares": [{"name": "Sarah", "cents": 1000}],
    }

    fake = FakeLlmClient([invalid])

    result = parse_turn(
        llm=fake,
        conversation=[
            user_message("Split our dinner")
        ],
        roster=ROSTER,
        current_user="Sarah",
    )

    assert result["type"] != "preview"


def test_full_conversation_history_retained():
    fake = FakeLlmClient([expense()])

    messages = [
        user_message("We shared pizza"),
        {
            "role": "assistant",
            "content": "How much was the pizza?",
        },
        user_message("It was $30 and Sarah paid"),
    ]

    parse_turn(
        llm=fake,
        conversation=messages,
        roster=ROSTER,
        current_user="Sarah",
    )

    assert len(fake.calls) == 1

    sent_messages = fake.calls[0]["messages"]

    assert sent_messages == messages
    assert len(sent_messages) == 3
