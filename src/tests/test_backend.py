
import pytest
from fastapi.testclient import TestClient

from backend.database import create_database, seed_database
from backend.repository import (
    list_groups,
    get_group,
    save_expense,
    list_expenses,
    create_conversation,
    get_conversation,
    update_conversation,
    delete_conversation,
)
from backend.main import create_app


@pytest.fixture
def db():
    connection = create_database(":memory:")
    seed_database(connection)
    yield connection
    connection.close()


@pytest.fixture
def client(db):
    app = create_app(
        db=db,
        session_secret="test-secret-with-at-least-32-characters",
    )
    with TestClient(app) as test_client:
        yield test_client


def get_apartment(db):
    return next(
        group for group in list_groups(db)
        if group["name"] == "Apartment 4B"
    )


# Issue #8: SQLite database

def test_apartment_roster(db):
    group = get_apartment(db)
    details = get_group(db, group["id"])

    assert details["members"] == [
        "Sarah", "Kayla", "Rui"
    ]


def test_weekend_trip_roster(db):
    group = next(
        group for group in list_groups(db)
        if group["name"] == "Weekend trip"
    )

    details = get_group(db, group["id"])

    assert details["members"] == [
        "Sarah", "Kayla", "Rui", "Aly", "Ben"
    ]


def test_seed_is_idempotent(db):
    before = list_groups(db)

    seed_database(db)
    seed_database(db)

    after = list_groups(db)

    assert len(after) == len(before)
    assert len({g["name"] for g in after}) == len(after)


def valid_saved_expense(group_id):
    return {
        "groupId": group_id,
        "description": "Dinner",
        "payer": "Sarah",
        "totalCents": 3000,
        "source": "manual",
        "createdBy": "Sarah",
        "shares": [
            {"name": "Sarah", "cents": 1000},
            {"name": "Kayla", "cents": 1000},
            {"name": "Rui", "cents": 1000},
        ],
    }


def test_save_expense_persists_shares(db):
    group = get_apartment(db)
    data = valid_saved_expense(group["id"])

    saved = save_expense(db, data)
    expenses = list_expenses(db, group["id"])

    expense = next(
        e for e in expenses if e["id"] == saved["id"]
    )

    assert expense["totalCents"] == 3000
    assert expense["shares"] == data["shares"]


def test_invalid_expense_not_saved(db):
    group = get_apartment(db)
    data = valid_saved_expense(group["id"])
    data["shares"][0]["cents"] = 999

    before = len(list_expenses(db, group["id"]))

    with pytest.raises(ValueError):
        save_expense(db, data)

    after = len(list_expenses(db, group["id"]))
    assert after == before


def test_transaction_rolls_back(db):
    group = get_apartment(db)
    data = valid_saved_expense(group["id"])

    data["shares"][2]["name"] = "Unknown"

    before = len(list_expenses(db, group["id"]))

    with pytest.raises(ValueError):
        save_expense(db, data)

    assert len(list_expenses(db, group["id"])) == before


def test_conversation_crud(db):
    group = get_apartment(db)

    created = create_conversation(db, {
        "groupId": group["id"],
        "userName": "Sarah",
        "promptCount": 1,
        "status": "pending",
    })

    conversation_id = created["id"]
    assert get_conversation(db, conversation_id)

    update_conversation(db, conversation_id, {
        "promptCount": 2,
        "status": "preview",
    })

    updated = get_conversation(db, conversation_id)
    assert updated["promptCount"] == 2
    assert updated["status"] == "preview"

    delete_conversation(db, conversation_id)
    assert get_conversation(db, conversation_id) is None


# Issue #9: Name-based sessions and groups

def test_public_name_picker(client):
    response = client.get("/api/session/names")

    assert response.status_code == 200
    names = str(response.json())

    for name in ["Sarah", "Kayla", "Rui"]:
        assert name in names


def test_valid_name_login(client):
    response = client.post(
        "/api/session", json={"name": "Sarah"}
    )

    assert response.status_code == 200
    assert "set-cookie" in response.headers

    cookie = response.headers["set-cookie"].lower()

    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_unknown_name_rejected(client):
    response = client.post(
        "/api/session", json={"name": "Unknown"}
    )
    assert response.status_code == 400


def test_protected_groups_require_login(client):
    response = client.get("/api/groups")
    assert response.status_code == 401



def test_tampered_session_rejected(client):
    # Log in to obtain a valid session cookie.
    response = client.post(
        "/api/session", json={"name": "Sarah"}
    )
    assert response.status_code == 200

    cookie_name = next(iter(client.cookies.keys()))
    original = client.cookies[cookie_name]

    # Remove all existing cookies so the original valid
    # cookie cannot accidentally be sent alongside
    # the tampered cookie.
    client.cookies.clear()

    # Send only the modified session cookie.
    client.cookies.set(
        cookie_name,
        original + "tampered",
    )

    response = client.get("/api/groups")

    assert response.status_code == 401



def test_session_identity_cannot_be_overridden(client):
    client.post("/api/session", json={"name": "Sarah"})

    response = client.get(
        "/api/session",
        params={"user": "Kayla"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Sarah"


def test_groups_available_after_login(client):
    client.post("/api/session", json={"name": "Sarah"})

    response = client.get("/api/groups")

    assert response.status_code == 200
    assert "Apartment 4B" in str(response.json())


def test_logout_invalidates_session(client):
    client.post("/api/session", json={"name": "Sarah"})

    response = client.delete("/api/session")
    assert response.status_code == 200

    response = client.get("/api/session")
    assert response.status_code == 401


@pytest.mark.parametrize("path", [
    "/api/groups",
    "/api/groups/1",
])
def test_known_protected_routes(client, path):
    response = client.get(path)
    assert response.status_code == 401
