from datetime import date

from pydantic import BaseModel, Field


class TradeRequest(BaseModel):
    trade_id: str = Field(min_length=1, max_length=100)
    version: int = Field(ge=1)
    counterparty_id: str = Field(min_length=1, max_length=100)
    book_id: str = Field(min_length=1, max_length=100)
    maturity_date: date


class TradeResponse(BaseModel):
    trade_id: str
    version: int
    counterparty_id: str
    book_id: str
    maturity_date: date
    created_date: date
    expired: bool = False


