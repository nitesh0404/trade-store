from datetime import date

from app.schemas.trade import TradeIn, TradeRecord


class TradeValidationError(ValueError):
    pass


def validate_and_prepare_trade(
    incoming: TradeIn,
    current: TradeRecord | None,
    *,
    today: date | None = None,
) -> TradeRecord:
    effective_today = today or date.today()

    if incoming.maturity_date < effective_today:
        raise TradeValidationError("maturity date cannot be before today")

    if current is not None and incoming.version < current.version:
        raise TradeValidationError("incoming version is lower than current version")

    return TradeRecord(
        trade_id=incoming.trade_id,
        version=incoming.version,
        maturity_date=incoming.maturity_date,
        created_date=effective_today,
    )
