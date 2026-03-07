from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db, init_db
from app.repositories.trade_repository import (
    get_latest_trade_by_id,
    save_trade,
)
from app.schemas.trade import TradeRequest, TradeResponse
from app.security.dependencies import require_trade_read, require_trade_write
from app.services.trade_service import TradeValidationError, validate_and_prepare_trade


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Trade Store API", lifespan=lifespan)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/trades",
    response_model=TradeResponse,
    tags=["trades"],
    dependencies=[Depends(require_trade_write)],
)
def upsert_trade(trade: TradeRequest, db: Session = Depends(get_db)) -> TradeResponse:
    current_entity = get_latest_trade_by_id(db, trade.trade_id)
    current = None
    if current_entity is not None:
        current = TradeResponse(
            trade_id=current_entity.trade_id,
            version=current_entity.version,
            counterparty_id=current_entity.counterparty_id,
            book_id=current_entity.book_id,
            maturity_date=current_entity.maturity_date,
            created_date=current_entity.created_date,
            expired=current_entity.expired,
        )

    try:
        record = validate_and_prepare_trade(incoming=trade, current=current)
    except TradeValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    saved = save_trade(db, record)
    return TradeResponse(
        trade_id=saved.trade_id,
        version=saved.version,
        counterparty_id=saved.counterparty_id,
        book_id=saved.book_id,
        maturity_date=saved.maturity_date,
        created_date=saved.created_date,
        expired=saved.expired,
    )


@app.get(
    "/trades/{trade_id}",
    response_model=TradeResponse,
    tags=["trades"],
    dependencies=[Depends(require_trade_read)],
)
def get_trade(trade_id: str, db: Session = Depends(get_db)) -> TradeResponse:
    trade = get_latest_trade_by_id(db, trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail="trade not found")

    return TradeResponse(
        trade_id=trade.trade_id,
        version=trade.version,
        counterparty_id=trade.counterparty_id,
        book_id=trade.book_id,
        maturity_date=trade.maturity_date,
        created_date=trade.created_date,
        expired=trade.expired,
    )
