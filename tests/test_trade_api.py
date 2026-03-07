from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app, trade_store


@pytest.fixture(autouse=True)
def clear_trade_store() -> None:
    trade_store.clear()
    yield
    trade_store.clear()


def test_post_trades_accepts_valid_trade_and_sets_created_date() -> None:
    client = TestClient(app)

    payload = {
        "trade_id": "API-100",
        "version": 1,
        "maturity_date": str(date.today() + timedelta(days=15)),
    }

    response = client.post("/trades", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["trade_id"] == payload["trade_id"]
    assert body["version"] == payload["version"]
    assert body["maturity_date"] == payload["maturity_date"]
    assert body["created_date"] == str(date.today())


def test_post_trades_rejects_lower_version_than_current_trade() -> None:
    client = TestClient(app)

    first_payload = {
        "trade_id": "API-200",
        "version": 3,
        "maturity_date": str(date.today() + timedelta(days=20)),
    }
    lower_version_payload = {
        "trade_id": "API-200",
        "version": 2,
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
        "maturity_date": str(date.today() - timedelta(days=1)),
    }

    response = client.post("/trades", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "maturity date cannot be before today"
