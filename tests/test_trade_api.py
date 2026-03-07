from collections.abc import Generator
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.db.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def clear_trade_store() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_post_trades_accepts_valid_trade_and_sets_created_date() -> None:
    client = TestClient(app)

    payload = {
        "trade_id": "API-100",
        "version": 1,
        "counterparty_id": "CP-API-1",
        "book_id": "BOOK-API-1",
        "maturity_date": str(date.today() + timedelta(days=15)),
    }

    response = client.post("/trades", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["trade_id"] == payload["trade_id"]
    assert body["version"] == payload["version"]
    assert body["counterparty_id"] == payload["counterparty_id"]
    assert body["book_id"] == payload["book_id"]
    assert body["maturity_date"] == payload["maturity_date"]
    assert body["created_date"] == str(date.today())


def test_post_trades_rejects_lower_version_than_current_trade() -> None:
    client = TestClient(app)

    first_payload = {
        "trade_id": "API-200",
        "version": 3,
        "counterparty_id": "CP-API-2",
        "book_id": "BOOK-API-2",
        "maturity_date": str(date.today() + timedelta(days=20)),
    }
    lower_version_payload = {
        "trade_id": "API-200",
        "version": 2,
        "counterparty_id": "CP-API-2",
        "book_id": "BOOK-API-2",
        "maturity_date": str(date.today() + timedelta(days=25)),
    }

    first_response = client.post("/trades", json=first_payload)
    assert first_response.status_code == 200

    response = client.post("/trades", json=lower_version_payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "incoming version is lower than current version"


def test_post_trades_rejects_maturity_date_before_today() -> None:
    client = TestClient(app)

    payload = {
        "trade_id": "API-300",
        "version": 1,
        "counterparty_id": "CP-API-3",
        "book_id": "BOOK-API-3",
        "maturity_date": str(date.today() - timedelta(days=1)),
    }

    response = client.post("/trades", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "maturity date cannot be before today"


def test_get_trade_returns_latest_trade_for_trade_id() -> None:
    client = TestClient(app)

    old_version_payload = {
        "trade_id": "API-400",
        "version": 1,
        "counterparty_id": "CP-API-4",
        "book_id": "BOOK-API-4",
        "maturity_date": str(date.today() + timedelta(days=10)),
    }
    latest_version_payload = {
        "trade_id": "API-400",
        "version": 2,
        "counterparty_id": "CP-API-4-UPDATED",
        "book_id": "BOOK-API-4-UPDATED",
        "maturity_date": str(date.today() + timedelta(days=20)),
    }

    create_old = client.post("/trades", json=old_version_payload)
    assert create_old.status_code == 200

    create_latest = client.post("/trades", json=latest_version_payload)
    assert create_latest.status_code == 200

    response = client.get("/trades/API-400")

    assert response.status_code == 200
    body = response.json()
    assert body["trade_id"] == "API-400"
    assert body["version"] == 2
    assert body["counterparty_id"] == "CP-API-4-UPDATED"
    assert body["book_id"] == "BOOK-API-4-UPDATED"
    assert body["maturity_date"] == latest_version_payload["maturity_date"]


def test_get_trade_returns_404_when_trade_id_does_not_exist() -> None:
    client = TestClient(app)

    response = client.get("/trades/UNKNOWN-TRADE")

    assert response.status_code == 404
    assert response.json()["detail"] == "trade not found"
