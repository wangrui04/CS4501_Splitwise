
import copy
import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError

from backend.schemas import (
    ParsedExpense,
    ExpensePreview,
    ChatResponse,
)
from backend.allocation import (
    parse_money_to_cents,
    format_cents,
    resolve_participants,
    allocate_items,
    split_cents,
    UnknownNameError,
)

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


# Issue #4: Pydantic schemas

def test_valid_expense_parses(valid_expense):
    result = ParsedExpense.model_validate(valid_expense)
    assert result.description == "Dinner"
    assert result.payer == "Sarah"


@pytest.mark.parametrize("quantity", [-1, 0, 1.5])
def test_invalid_quantities(valid_expense, quantity):
    data = copy.deepcopy(valid_expense)
    data["items"][0]["quantity"] = quantity

    with pytest.raises(ValidationError):
        ParsedExpense.model_validate(data)


@pytest.mark.parametrize(
    "price", ["12.345", "-5", "abc"]
)
def test_invalid_prices(valid_expense, price):
    data = copy.deepcopy(valid_expense)
    data["items"][0]["unitPrice"] = price

    with pytest.raises(ValidationError):
        ParsedExpense.model_validate(data)


def test_reject_unknown_participant_mode(valid_expense):
    data = copy.deepcopy(valid_expense)
    data["items"][0]["participants"]["mode"] = "random"

    with pytest.raises(ValidationError):
        ParsedExpense.model_validate(data)


@pytest.mark.parametrize(
    "extra_field",
    [{"shares": [1000, 1000, 1000]}, {"totalCents": 3000}],
)
def test_llm_cannot_supply_calculated_fields(
    valid_expense, extra_field
):
    data = {**valid_expense, **extra_field}

    with pytest.raises(ValidationError):
        ParsedExpense.model_validate(data)


def test_null_price_and_payer_allowed(valid_expense):
    data = copy.deepcopy(valid_expense)
    data["payer"] = None
    data["items"][0]["unitPrice"] = None

    result = ParsedExpense.model_validate(data)

    assert result.payer is None
    assert result.items[0].unitPrice is None


def test_charge_cannot_have_amount_and_percent(valid_expense):
    data = copy.deepcopy(valid_expense)
    data["charges"] = [{
        "kind": "tip",
        "amount": "5.00",
        "percent": "20",
        "method": "equal",
    }]

    with pytest.raises(ValidationError):
        ParsedExpense.model_validate(data)


def test_valid_preview():
    preview = {
        "payer": "Sarah",
        "currency": "USD",
        "lineItems": [],
        "charges": [],
        "totalCents": 3000,
        "shares": [
            {"name": name, "cents": 1000, "summary": "Pizza"}
            for name in ROSTER
        ],
        "validated": True,
    }

    result = ExpensePreview.model_validate(preview)
    assert result.totalCents == 3000
    assert result.validated is True


@pytest.mark.parametrize(
    "response_type",
    ["question", "preview", "unresolved", "error"],
)
def test_chat_response_union_has_all_types(response_type):
    from typing import get_args

    variants = get_args(ChatResponse)
    accepted = set()

    for variant in variants:
        field = variant.model_fields["type"]
        accepted.update(get_args(field.annotation))

    assert response_type in accepted


# Issue #5: Money handling

@pytest.mark.parametrize("value,expected", [
    ("12.50", 1250),
    ("12", 1200),
    ("$12", 1200),
    ("0", 0),
    (".5", 50),
    ("0.01", 1),
])
def test_parse_money(value, expected):
    assert parse_money_to_cents(value) == expected


@pytest.mark.parametrize(
    "value", ["12.345", "-5", "abc", "NaN"]
)
def test_reject_invalid_money(value):
    with pytest.raises(ValueError):
        parse_money_to_cents(value)


def test_format_money():
    assert format_cents(1250) == "$12.50"
    assert format_cents(0) == "$0.00"
    assert format_cents(1234567) == "$12,345.67"


# Issue #5: Participants

def test_all_members():
    spec = {"mode": "all", "names": []}
    assert resolve_participants(spec, ROSTER, "Sarah") == ROSTER


def test_only_selected_members():
    spec = {"mode": "only", "names": ["Kayla", "Rui"]}
    assert resolve_participants(spec, ROSTER, "Sarah") == [
        "Kayla", "Rui"
    ]


def test_everyone_except_member():
    spec = {"mode": "all_except", "names": ["Kayla"]}
    assert resolve_participants(spec, ROSTER, "Sarah") == [
        "Sarah", "Rui"
    ]


def test_me_resolves_to_signed_in_user():
    spec = {"mode": "only", "names": ["ME"]}
    assert resolve_participants(spec, ROSTER, "Kayla") == [
        "Kayla"
    ]


def test_unknown_name_rejected():
    spec = {"mode": "only", "names": ["Ben"]}

    with pytest.raises(UnknownNameError):
        resolve_participants(spec, ROSTER, "Sarah")


# Issue #5: Allocations

def test_equal_split(valid_expense):
    result = allocate_items(
        valid_expense["items"], "Sarah", ROSTER, "Sarah"
    )

    assert result["totalCents"] == 3000
    assert result["shares"] == {
        "Sarah": 1000,
        "Kayla": 1000,
        "Rui": 1000,
    }


def test_split_between_two_members(valid_expense):
    item = copy.deepcopy(valid_expense["items"][0])
    item["unitPrice"] = "24.00"
    item["participants"] = {
        "mode": "only",
        "names": ["Kayla", "Rui"],
    }

    result = allocate_items(
        [item], "Sarah", ROSTER, "Sarah"
    )

    assert result["shares"] == {
        "Sarah": 0,
        "Kayla": 1200,
        "Rui": 1200,
    }


def test_quantity_multiplies_price(valid_expense):
    item = copy.deepcopy(valid_expense["items"][0])
    item["quantity"] = 2
    item["unitPrice"] = "10.00"

    result = allocate_items(
        [item], "Sarah", ROSTER, "Sarah"
    )
    assert result["totalCents"] == 2000


def test_different_items_for_each_person():
    items = []

    for name, price in [
        ("Sarah", "6.00"),
        ("Kayla", "21.00"),
        ("Rui", "15.00"),
    ]:
        items.append({
            "name": f"{name}'s meal",
            "quantity": 1,
            "unitPrice": price,
            "participants": {
                "mode": "only",
                "names": [name],
            },
        })

    result = allocate_items(
        items, "Sarah", ROSTER, "Sarah"
    )

    assert result["shares"] == {
        "Sarah": 600,
        "Kayla": 2100,
        "Rui": 1500,
    }
    assert result["totalCents"] == 4200


# Issue #6: Deterministic rounding

def test_payer_receives_extra_cent():
    result = split_cents(
        1000, [1, 1, 1], ROSTER, "Sarah", ROSTER
    )
    assert result == {
        "Sarah": 334,
        "Kayla": 333,
        "Rui": 333,
    }


def test_roster_order_breaks_ties():
    members = ["Sarah", "Kayla", "Rui", "Ben"]

    result = split_cents(
        1000,
        [1, 1, 1],
        ["Kayla", "Rui", "Ben"],
        "Sarah",
        members,
    )

    assert result == {
        "Kayla": 334,
        "Rui": 333,
        "Ben": 333,
    }


@pytest.mark.parametrize("amount,expected", [
    (1, {"Sarah": 1, "Kayla": 0, "Rui": 0}),
    (2, {"Sarah": 1, "Kayla": 1, "Rui": 0}),
])
def test_small_amount_rounding(amount, expected):
    result = split_cents(
        amount, [1, 1, 1], ROSTER, "Ben", ROSTER
    )
    assert result == expected


def test_weighted_rounding():
    result = split_cents(
        100,
        [1, 2],
        ["Kayla", "Rui"],
        "Sarah",
        ROSTER,
    )
    assert result == {"Kayla": 33, "Rui": 67}


@given(
    amount=st.integers(min_value=0, max_value=100000),
    count=st.integers(min_value=1, max_value=5),
)
def test_split_never_creates_or_loses_money(amount, count):
    members = ["A", "B", "C", "D", "E"][:count]

    result = split_cents(
        amount,
        [1] * count,
        members,
        "Payer",
        members,
    )

    assert sum(result.values()) == amount
    assert all(
        isinstance(value, int) and value >= 0
        for value in result.values()
    )
