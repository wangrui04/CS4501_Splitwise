
import copy
import pytest
from hypothesis import given, strategies as st

from backend.validator import validate, question_for_error

ROSTER = ["Sarah", "Kayla", "Rui"]


@pytest.fixture
def valid_expense():
    return {
        "description": "Dinner",
        "payer": "Sarah",
        "items": [{
            "name": "Pizza",
            "quantity": 1,
            "unitPrice": "30.00",
            "participants": {
                "mode": "all",
                "names": [],
            },
        }],
        "charges": [],
        "statedTotal": "30.00",
        "openQuestions": [],
    }


@pytest.fixture
def valid_allocation():
    return {
        "totalCents": 3000,
        "shares": {
            "Sarah": 1000,
            "Kayla": 1000,
            "Rui": 1000,
        },
    }


def assert_error(result, code):
    assert result["ok"] is False
    assert code in [
        error["code"] for error in result["errors"]
    ]


def test_valid_expense_passes(valid_expense, valid_allocation):
    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert result == {"ok": True}


def test_shares_do_not_sum(valid_expense, valid_allocation):
    valid_allocation["shares"]["Sarah"] = 999

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "SHARES_DONT_SUM")


def test_non_positive_total(valid_expense, valid_allocation):
    valid_allocation["totalCents"] = 0
    valid_allocation["shares"] = {
        name: 0 for name in ROSTER
    }

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "NON_POSITIVE_TOTAL")


def test_negative_amount(valid_expense, valid_allocation):
    valid_allocation["shares"]["Sarah"] = -100

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "NEGATIVE_AMOUNT")


def test_unknown_name(valid_expense, valid_allocation):
    valid_expense["items"][0]["participants"] = {
        "mode": "only",
        "names": ["Ben"],
    }

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "UNKNOWN_NAME")


def test_missing_payer(valid_expense, valid_allocation):
    valid_expense["payer"] = None

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "MISSING_PAYER")


def test_missing_price(valid_expense, valid_allocation):
    valid_expense["items"][0]["unitPrice"] = None

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "MISSING_PRICE")


def test_no_participants(valid_expense, valid_allocation):
    valid_expense["items"][0]["participants"] = {
        "mode": "only",
        "names": [],
    }

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "NO_PARTICIPANTS")


def test_missing_tax_tip_method(
    valid_expense, valid_allocation
):
    valid_expense["charges"] = [{
        "kind": "tip",
        "amount": "5.00",
        "percent": None,
        "method": None,
    }]

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "TAX_TIP_METHOD_MISSING")


def test_stated_total_mismatch(
    valid_expense, valid_allocation
):
    valid_expense["statedTotal"] = "40.00"
    valid_expense["items"][0]["unitPrice"] = "42.00"

    valid_allocation["totalCents"] = 4200
    valid_allocation["shares"] = {
        name: 1400 for name in ROSTER
    }

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )

    assert_error(result, "STATED_TOTAL_MISMATCH")

    error = next(
        e for e in result["errors"]
        if e["code"] == "STATED_TOTAL_MISMATCH"
    )

    assert "40" in error["message"]
    assert "42" in error["message"]


def test_non_integer_cents(valid_expense, valid_allocation):
    valid_allocation["shares"]["Sarah"] = 1000.5

    result = validate(
        valid_expense, valid_allocation, ROSTER
    )
    assert_error(result, "NON_INTEGER_CENTS")


def test_missing_price_follow_up():
    error = {
        "code": "MISSING_PRICE",
        "field": "items[0].unitPrice",
        "message": "Missing price for Pizza",
    }

    question = question_for_error(error)

    assert "pizza" in question.lower()
    assert "how much" in question.lower()


def test_unknown_name_follow_up():
    error = {
        "code": "UNKNOWN_NAME",
        "field": "items[0].participants",
        "message": "Unknown member Ben",
    }

    question = question_for_error(error)
    assert "Ben" in question


@pytest.mark.parametrize("code", [
    "SHARES_DONT_SUM",
    "NON_POSITIVE_TOTAL",
    "NEGATIVE_AMOUNT",
    "UNKNOWN_NAME",
    "MISSING_PAYER",
    "MISSING_PRICE",
    "NO_PARTICIPANTS",
    "TAX_TIP_METHOD_MISSING",
    "STATED_TOTAL_MISMATCH",
    "NON_INTEGER_CENTS",
])
def test_every_error_has_follow_up(code):
    error = {
        "code": code,
        "field": "expense",
        "message": f"Validation error: {code}",
    }

    question = question_for_error(error)

    assert isinstance(question, str)
    assert question.strip()


@given(
    total=st.integers(min_value=1, max_value=100000),
    difference=st.integers(min_value=1, max_value=1000),
)
def test_invalid_share_sum_always_rejected(
    total, difference
):
    expense = {
        "description": "Property test",
        "payer": "Sarah",
        "items": [{
            "name": "Item",
            "quantity": 1,
            "unitPrice": "1.00",
            "participants": {
                "mode": "all",
                "names": [],
            },
        }],
        "charges": [],
        "statedTotal": None,
        "openQuestions": [],
    }

    allocation = {
        "totalCents": total,
        "shares": {
            "Sarah": total + difference,
            "Kayla": 0,
            "Rui": 0,
        },
    }

    result = validate(expense, allocation, ROSTER)
    assert_error(result, "SHARES_DONT_SUM")
