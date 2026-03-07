from datetime import date

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TradeModel(Base):
    __tablename__ = "trades"

    trade_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    counterparty_id: Mapped[str] = mapped_column(String, nullable=False)
    book_id: Mapped[str] = mapped_column(String, nullable=False)
    maturity_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_date: Mapped[date] = mapped_column(Date, nullable=False)
    expired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
