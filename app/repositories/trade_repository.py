from datetime import date

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.trade import TradeModel
from app.schemas.trade import TradeResponse


def get_latest_trade_by_id(session: Session, trade_id: str) -> TradeModel | None:
    statement = (
        select(TradeModel)
        .where(TradeModel.trade_id == trade_id)
        .order_by(TradeModel.version.desc())
        .limit(1)
    )
    return session.scalar(statement)


def get_trade_by_id_and_version(session: Session, trade_id: str, version: int) -> TradeModel | None:
    statement = select(TradeModel).where(
        TradeModel.trade_id == trade_id,
        TradeModel.version == version,
    )
    return session.scalar(statement)


def save_trade(session: Session, trade: TradeResponse) -> TradeModel:
    entity = get_trade_by_id_and_version(session, trade.trade_id, trade.version)
    expired = trade.maturity_date < date.today()

    if entity is None:
        entity = TradeModel(
            trade_id=trade.trade_id,
            version=trade.version,
            counterparty_id=trade.counterparty_id,
            book_id=trade.book_id,
            maturity_date=trade.maturity_date,
            created_date=trade.created_date,
            expired=expired,
        )
        session.add(entity)
    else:
        entity.counterparty_id = trade.counterparty_id
        entity.book_id = trade.book_id
        entity.maturity_date = trade.maturity_date
        entity.created_date = trade.created_date
        entity.expired = expired

    session.commit()
    session.refresh(entity)
    return entity


def mark_expired_trades(session: Session, *, today: date | None = None) -> int:
    effective_today = today or date.today()
    statement = (
        update(TradeModel)
        .where(TradeModel.expired.is_(False), TradeModel.maturity_date < effective_today)
        .values(expired=True)
    )
    result = session.execute(statement)
    session.commit()
    return int(result.rowcount or 0)
