
import sqlite3


def create_database(path=":memory:"):
    db = sqlite3.connect(
        path,
        check_same_thread=False,
    )
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS group_members (
            group_id INTEGER NOT NULL REFERENCES groups(id),
            name TEXT NOT NULL,
            position INTEGER NOT NULL,
            PRIMARY KEY(group_id, name)
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            group_id INTEGER NOT NULL REFERENCES groups(id),
            description TEXT NOT NULL,
            payer_name TEXT NOT NULL,
            total_cents INTEGER NOT NULL,
            source TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS expense_shares (
            expense_id INTEGER NOT NULL REFERENCES expenses(id),
            name TEXT NOT NULL,
            cents INTEGER NOT NULL,
            PRIMARY KEY(expense_id, name)
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            group_id INTEGER NOT NULL REFERENCES groups(id),
            user_name TEXT NOT NULL,
            prompt_count INTEGER NOT NULL,
            status TEXT NOT NULL,
            final_preview_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    return db


def seed_database(db):
    groups = [
        (
            "Apartment 4B",
            ["Sarah", "Kayla", "Rui"],
        ),
        (
            "Weekend trip",
            ["Sarah", "Kayla", "Rui", "Aly", "Ben"],
        ),
    ]

    with db:
        for group_name, members in groups:
            db.execute(
                "INSERT OR IGNORE INTO groups(name) VALUES(?)",
                (group_name,),
            )

            row = db.execute(
                "SELECT id FROM groups WHERE name=?",
                (group_name,),
            ).fetchone()

            group_id = row["id"]

            for position, name in enumerate(members):
                db.execute(
                    """
                    INSERT OR IGNORE INTO group_members
                    (group_id, name, position)
                    VALUES (?, ?, ?)
                    """,
                    (group_id, name, position),
                )
