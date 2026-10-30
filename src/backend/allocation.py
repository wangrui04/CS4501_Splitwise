
from __future__ import annotations

from decimal import Decimal
from typing import Any
import re


class UnknownNameError(ValueError):
    def __init__(self, name):
        self.name = name
        super().__init__(f"Unknown group member: {name}")


_MONEY = re.compile(
    r"^\$?(?:\d+(?:\.\d{1,2})?|\.\d{1,2})$"
)


def parse_money_to_cents(value: str) -> int:
    if not isinstance(value, str) or not _MONEY.fullmatch(value):
        raise ValueError(f"Invalid money amount: {value!r}")

    cents = Decimal(value.removeprefix("$")) * 100
    return int(cents)


def format_cents(cents: int) -> str:
    if not isinstance(cents, int):
        raise ValueError("Cents must be an integer")

    sign = "-" if cents < 0 else ""
    dollars = abs(cents) // 100
    remainder = abs(cents) % 100

    return f"{sign}${dollars:,}.{remainder:02d}"


def resolve_participants(
    spec: Any,
    roster: list[str],
    current_user: str,
) -> list[str]:
    if hasattr(spec, "model_dump"):
        spec = spec.model_dump()

    mode = spec["mode"]
    names = spec["names"]

    resolved = [
        current_user if name == "ME" else name
        for name in names
    ]

    for name in resolved:
        if name not in roster:
            raise UnknownNameError(name)

    if mode == "all":
        return list(roster)

    if mode == "only":
        return list(dict.fromkeys(resolved))

    if mode == "all_except":
        return [
            name for name in roster
            if name not in resolved
        ]

    raise ValueError("Unknown participant mode")


def split_cents(
    amount_cents: int,
    weights: list[int],
    sharers: list[str],
    payer: str,
    roster_order: list[str],
) -> dict[str, int]:
    if type(amount_cents) is not int or amount_cents < 0:
        raise ValueError(
            "Amount must be nonnegative integer cents"
        )

    if (
        not sharers
        or len(weights) != len(sharers)
        or len(set(sharers)) != len(sharers)
    ):
        raise ValueError("Invalid sharers")

    if (
        any(type(w) is not int or w < 0 for w in weights)
        or not sum(weights)
    ):
        raise ValueError(
            "Weights must be nonnegative integers with positive sum"
        )

    total_weight = sum(weights)

    base = {
        name: amount_cents * weight // total_weight
        for name, weight in zip(sharers, weights)
    }

    leftover = amount_cents - sum(base.values())

    if payer in sharers:
        base[payer] += leftover
    else:
        order = {
            name: index
            for index, name in enumerate(roster_order)
        }

        ranked = sorted(
            sharers,
            key=lambda name: (
                -(
                    amount_cents
                    * weights[sharers.index(name)]
                    % total_weight
                ),
                order.get(name, len(order)),
            ),
        )

        for name in ranked[:leftover]:
            base[name] += 1

    return base


def allocate_items(
    items: list,
    payer: str,
    roster: list[str],
    current_user: str,
) -> dict:
    shares = {name: 0 for name in roster}
    total = 0
    line_items = []

    for raw in items:
        item = (
            raw.model_dump()
            if hasattr(raw, "model_dump")
            else raw
        )

        if item["unitPrice"] is None:
            raise ValueError("Missing item price")

        count = item["quantity"]

        if type(count) is not int or count < 1:
            raise ValueError("Invalid quantity")

        cents = parse_money_to_cents(
            item["unitPrice"]
        ) * count

        sharers = resolve_participants(
            item["participants"],
            roster,
            current_user,
        )

        if not sharers:
            raise ValueError("No participants")

        allocation = split_cents(
            cents,
            [1] * len(sharers),
            sharers,
            payer,
            roster,
        )

        for name, amount in allocation.items():
            shares[name] += amount

        line_items.append({
            "name": item["name"],
            "totalCents": cents,
            "shares": allocation,
        })

        total += cents

    return {
        "totalCents": total,
        "shares": shares,
        "lineItems": line_items,
    }
