from datetime import date

from pydantic import BaseModel, Field


class TradeIn(BaseModel):
    trade_id: str = Field(min_length=1, max_length=100)
    version: int = Field(ge=1)
    maturity_date: date


class TradeRecord(BaseModel):
    trade_id: str
    version: int
    maturity_date: date
    created_date: date
