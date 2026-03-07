from collections.abc import Generator
from datetime import date, timedelta

import pytest

from app.db.database import Base, engine
from app.repositories.trade_repository import mark_expired_trades, save_trade
from app.db.database import SessionLocal
from app.schemas.trade import TradeResponse


@pytest.fixture(autouse=True)
def clear_trade_store() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_mark_expired_trades_updates_records_past_maturity(db_session) -> None:
    """Trades whose maturity_date is before today should be marked expired."""
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)

    # Arrange: insert an already-matured trade and a still-valid trade.
    # We use save_trade which sets expired at save time, so we create
    # a trade with a future maturity first, then manually set maturity back.
    expired_trade = TradeResponse(
        trade_id="EXP-1",
        version=1,
        counterparty_id="CP-1",
        book_id="BOOK-1",
        maturity_date=yesterday,
        created_date=date.today() - timedelta(days=10),
        expired=False,
    )
    valid_trade = TradeResponse(
        trade_id="VALID-1",
        version=1,
        counterparty_id="CP-2",
        book_id="BOOK-2",
        maturity_date=tomorrow,
        created_date=date.today(),
        expired=False,
    )

    # Save both trades via repository (save_trade sets expired based on today)
    save_trade(db_session, expired_trade)
    save_trade(db_session, valid_trade)

    # Forcefully reset the expired flag to FALSE so we can test mark_expired_trades
    from app.models.trade import TradeModel
    db_session.query(TradeModel).filter(TradeModel.trade_id == "EXP-1").update({"expired": False})
    db_session.commit()

    # Act
    count = mark_expired_trades(db_session, today=date.today())

    # Assert
    assert count == 1

    from sqlalchemy import select
    expired = db_session.scalar(
        select(TradeModel).where(TradeModel.trade_id == "EXP-1")
    )
    valid = db_session.scalar(
        select(TradeModel).where(TradeModel.trade_id == "VALID-1")
    )
    assert expired.expired is True
    assert valid.expired is False


def test_mark_expired_trades_returns_zero_when_nothing_to_expire(db_session) -> None:
    """When all trades have future maturity dates, nothing should be marked expired."""
    future_trade = TradeResponse(
        trade_id="FUTURE-1",
        version=1,
        counterparty_id="CP-3",
        book_id="BOOK-3",
        maturity_date=date.today() + timedelta(days=30),
        created_date=date.today(),
        expired=False,
    )
    save_trade(db_session, future_trade)

    count = mark_expired_trades(db_session, today=date.today())

    assert count == 0
