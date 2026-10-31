
from decimal import Decimal, ROUND_HALF_UP

from backend.schemas import ParsedExpense
from backend.allocation import (
    allocate_items,
    resolve_participants,
    UnknownNameError,
    split_cents,
    parse_money_to_cents,
)
from backend.validator import validate, question_for_error


def parse_turn(*, llm, conversation, roster, current_user):
    try:
        raw = llm.parse(
            messages=conversation,
            roster=roster,
            current_user=current_user,
        )
        parsed = ParsedExpense.model_validate(raw)

    except Exception:
        return {
            "type": "unresolved",
            "reason": (
                "Unable to parse a valid structured expense"
            ),
        }

    data = parsed.model_dump()

    if data["openQuestions"]:
        return {
            "type": "question",
            "question": data["openQuestions"][0]["question"],
        }

    payer = (
        current_user
        if data["payer"] == "ME"
        else data["payer"]
    )

    data["payer"] = payer

    if payer is None:
        return {
            "type": "question",
            "question": "Who paid for this expense?",
        }

    if payer not in roster:
        return {
            "type": "question",
            "question": (
                f"Unknown member {payer}. Who paid?"
            ),
        }

    for item in data["items"]:
        if item["unitPrice"] is None:
            return {
                "type": "question",
                "question": (
                    f"How much was {item['name']}?"
                ),
            }

        try:
            sharers = resolve_participants(
                item["participants"],
                roster,
                current_user,
            )

            if not sharers:
                return {
                    "type": "question",
                    "question": (
                        f"Who should share {item['name']}?"
                    ),
                }

        except UnknownNameError as error:
            return {
                "type": "question",
                "question": (
                    f"Unknown member {error.name}. "
                    "Who did you mean?"
                ),
            }

    try:
        allocation = allocate_items(
            data["items"],
            payer,
            roster,
            current_user,
        )

        # All tax, tip, and fee arithmetic happens here,
        # not inside the LLM.
        for charge in data["charges"]:
            if charge["method"] is None:
                return {
                    "type": "question",
                    "question": (
                        "Should tax or tip be split "
                        "equally or proportionally?"
                    ),
                }

            if (
                charge["amount"] is None
                and charge["percent"] is None
            ):
                return {
                    "type": "question",
                    "question": (
                        f"How much was the {charge['kind']}?"
                    ),
                }

            if charge["amount"] is not None:
                cents = parse_money_to_cents(
                    charge["amount"]
                )
            else:
                percentage = Decimal(
                    charge["percent"]
                )

                cents = int(
                    (
                        Decimal(allocation["totalCents"])
                        * percentage
                        / 100
                    ).quantize(
                        Decimal("1"),
                        rounding=ROUND_HALF_UP,
                    )
                )

            active = [
                name for name in roster
                if allocation["shares"][name] > 0
            ]

            if not active:
                active = list(roster)

            if charge["method"] == "proportional":
                weights = [
                    allocation["shares"][name]
                    for name in active
                ]
            else:
                weights = [1] * len(active)

            splits = split_cents(
                cents,
                weights,
                active,
                payer,
                roster,
            )

            for name, amount in splits.items():
                allocation["shares"][name] += amount

            allocation["totalCents"] += cents

        result = validate(
            data,
            allocation,
            roster,
        )

    except (ValueError, ZeroDivisionError) as exc:
        return {
            "type": "question",
            "question": (
                f"Please clarify this expense: {exc}"
            ),
        }

    if not result["ok"]:
        return {
            "type": "question",
            "question": question_for_error(
                result["errors"][0]
            ),
        }

    preview = {
        "payer": payer,
        "currency": "USD",
        "lineItems": allocation["lineItems"],
        "charges": data["charges"],
        "totalCents": allocation["totalCents"],
        "shares": [
            {
                "name": name,
                "cents": allocation["shares"][name],
                "summary": data["description"],
            }
            for name in roster
        ],
        "validated": True,
    }

    return {
        "type": "preview",
        "preview": preview,
    }
