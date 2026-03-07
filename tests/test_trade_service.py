from datetime import date, timedelta

import pytest

from app.schemas.trade import TradeRequest, TradeResponse
from app.services.trade_service import TradeValidationError, validate_and_prepare_trade


def test_v1_rejects_when_incoming_version_is_lower_than_current() -> None:
    current = TradeResponse(
        trade_id="T-100",
        version=5,
        counterparty_id="CP-1",
        book_id="BOOK-1",
        maturity_date=date.today() + timedelta(days=20),
        created_date=date.today(),
    )
    incoming = TradeRequest(
        trade_id="T-100",
        version=4,
        counterparty_id="CP-1",
        book_id="BOOK-1",
        maturity_date=date.today() + timedelta(days=30),
    )

    with pytest.raises(TradeValidationError, match="lower than current version"):
        validate_and_prepare_trade(incoming=incoming, current=current)


def test_v2_replaces_record_when_version_is_the_same() -> None:
    current = TradeResponse(
        trade_id="T-200",
        version=3,
        counterparty_id="CP-2",
        book_id="BOOK-2",
        maturity_date=date.today() + timedelta(days=10),
        created_date=date.today() - timedelta(days=2),
    )
    incoming = TradeRequest(
        trade_id="T-200",
        version=3,
        counterparty_id="CP-NEW",
        book_id="BOOK-NEW",
        maturity_date=date.today() + timedelta(days=40),
    )

    result = validate_and_prepare_trade(incoming=incoming, current=current)

    assert result.trade_id == "T-200"
    assert result.version == 3
    assert result.counterparty_id == "CP-NEW"
    assert result.book_id == "BOOK-NEW"
    assert result.maturity_date == incoming.maturity_date
    assert result.created_date == date.today()


def test_v3_rejects_when_maturity_date_is_before_today() -> None:
    incoming = TradeRequest(
        trade_id="T-300",
        version=1,
        counterparty_id="CP-3",
        book_id="BOOK-3",
        maturity_date=date.today() - timedelta(days=1),
    )

    with pytest.raises(TradeValidationError, match="maturity date cannot be before today"):
        validate_and_prepare_trade(incoming=incoming, current=None)
