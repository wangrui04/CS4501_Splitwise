
import json


def list_groups(db):
    rows = db.execute(
        "SELECT id, name FROM groups ORDER BY id"
    )
    return [dict(row) for row in rows]


def get_group(db, group_id):
    row = db.execute(
        "SELECT id, name FROM groups WHERE id=?",
        (group_id,),
    ).fetchone()

    if row is None:
        return None

    result = dict(row)

    members = db.execute(
        """
        SELECT name FROM group_members
        WHERE group_id=?
        ORDER BY position
        """,
        (group_id,),
    )

    result["members"] = [
        member["name"] for member in members
    ]

    return result


def save_expense(db, data):
    group = get_group(db, data["groupId"])

    if group is None:
        raise ValueError("Unknown group")

    members = set(group["members"])
    shares = data["shares"]
    total = data["totalCents"]

    if (
        type(total) is not int
        or total <= 0
        or not shares
        or any(
            type(share["cents"]) is not int
            or share["cents"] < 0
            for share in shares
        )
    ):
        raise ValueError("Invalid cents")

    if sum(
        share["cents"] for share in shares
    ) != total:
        raise ValueError("Shares do not sum to total")

    if (
        data["payer"] not in members
        or data["createdBy"] not in members
        or any(
            share["name"] not in members
            for share in shares
        )
    ):
        raise ValueError("Unknown member")

    if len({
        share["name"] for share in shares
    }) != len(shares):
        raise ValueError("Duplicate shares")

    if data["source"] not in ("ai", "manual"):
        raise ValueError("Invalid source")

    with db:
        cursor = db.execute(
            """
            INSERT INTO expenses (
                group_id,
                description,
                payer_name,
                total_cents,
                source,
                created_by
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["groupId"],
                data["description"],
                data["payer"],
                total,
                data["source"],
                data["createdBy"],
            ),
        )

        expense_id = cursor.lastrowid

        for share in shares:
            db.execute(
                """
                INSERT INTO expense_shares
                (expense_id, name, cents)
                VALUES (?, ?, ?)
                """,
                (
                    expense_id,
                    share["name"],
                    share["cents"],
                ),
            )

    return {"id": expense_id}


def list_expenses(db, group_id):
    result = []

    rows = db.execute(
        """
        SELECT * FROM expenses
        WHERE group_id=?
        ORDER BY id
        """,
        (group_id,),
    ).fetchall()

    for row in rows:
        expense = dict(row)

        # Convert SQLite column names to API field names.
        expense["totalCents"] = expense.pop("total_cents")
        expense["groupId"] = expense.pop("group_id")
        expense["payer"] = expense.pop("payer_name")
        expense["createdBy"] = expense.pop("created_by")

        share_rows = db.execute(
            """
            SELECT name, cents
            FROM expense_shares
            WHERE expense_id=?
            ORDER BY rowid
            """,
            (expense["id"],),
        )

        expense["shares"] = [
            {
                "name": share["name"],
                "cents": share["cents"],
            }
            for share in share_rows
        ]

        result.append(expense)

    return result


def create_conversation(db, data):
    with db:
        cursor = db.execute(
            """
            INSERT INTO conversations
            (group_id, user_name, prompt_count, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                data["groupId"],
                data["userName"],
                data["promptCount"],
                data["status"],
            ),
        )

    return {"id": cursor.lastrowid}


def get_conversation(db, conversation_id):
    row = db.execute(
        "SELECT * FROM conversations WHERE id=?",
        (conversation_id,),
    ).fetchone()

    if row is None:
        return None

    result = dict(row)

    return {
        "id": result["id"],
        "groupId": result["group_id"],
        "userName": result["user_name"],
        "promptCount": result["prompt_count"],
        "status": result["status"],
        "finalPreview": (
            json.loads(result["final_preview_json"])
            if result["final_preview_json"]
            else None
        ),
    }


def update_conversation(db, conversation_id, data):
    mapping = {
        "promptCount": "prompt_count",
        "status": "status",
        "finalPreview": "final_preview_json",
    }

    fields = []
    values = []

    for key, value in data.items():
        if key not in mapping:
            raise ValueError("Unknown field")

        fields.append(mapping[key] + "=?")

        if key == "finalPreview":
            value = json.dumps(value)

        values.append(value)

    if not fields:
        return

    values.append(conversation_id)

    with db:
        db.execute(
            f"""
            UPDATE conversations
            SET {", ".join(fields)},
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            values,
        )


def delete_conversation(db, conversation_id):
    with db:
        db.execute(
            "DELETE FROM conversations WHERE id=?",
            (conversation_id,),
        )
