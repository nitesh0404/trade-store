from fastapi import FastAPI, HTTPException

from app.schemas.trade import TradeIn, TradeRecord
from app.services.trade_service import TradeValidationError, validate_and_prepare_trade


app = FastAPI(title="Trade Store API")
trade_store: dict[str, TradeRecord] = {}


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/trades", response_model=TradeRecord, tags=["trades"])
def upsert_trade(trade: TradeIn) -> TradeRecord:
    current = trade_store.get(trade.trade_id)

    try:
        record = validate_and_prepare_trade(incoming=trade, current=current)
    except TradeValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    trade_store[trade.trade_id] = record
    return record
