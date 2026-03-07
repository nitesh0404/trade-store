from datetime import date, timedelta

import pytest

from app.schemas.trade import TradeIn, TradeRecord
from app.services.trade_service import TradeValidationError, validate_and_prepare_trade


def test_v1_rejects_when_incoming_version_is_lower_than_current() -> None:
    current = TradeRecord(
        trade_id="T-100",
        version=5,
        maturity_date=date.today() + timedelta(days=20),
        created_date=date.today(),
    )
    incoming = TradeIn(
        trade_id="T-100",
        version=4,
        maturity_date=date.today() + timedelta(days=30),
    )

    with pytest.raises(TradeValidationError, match="lower than current version"):
        validate_and_prepare_trade(incoming=incoming, current=current)


def test_v2_replaces_record_when_version_is_the_same() -> None:
    current = TradeRecord(
        trade_id="T-200",
        version=3,
        maturity_date=date.today() + timedelta(days=10),
        created_date=date.today() - timedelta(days=2),
    )
    incoming = TradeIn(
        trade_id="T-200",
        version=3,
        maturity_date=date.today() + timedelta(days=40),
    )

    result = validate_and_prepare_trade(incoming=incoming, current=current)

    assert result.trade_id == "T-200"
    assert result.version == 3
    assert result.maturity_date == incoming.maturity_date
    assert result.created_date == date.today()


def test_v3_rejects_when_maturity_date_is_before_today() -> None:
    incoming = TradeIn(
        trade_id="T-300",
        version=1,
        maturity_date=date.today() - timedelta(days=1),
    )

    with pytest.raises(TradeValidationError, match="maturity date cannot be before today"):
        validate_and_prepare_trade(incoming=incoming, current=None)
