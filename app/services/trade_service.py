from datetime import date

from app.schemas.trade import TradeRequest, TradeResponse


class TradeValidationError(ValueError):
    def __init__(self, message: str, *, reason: str, context: dict[str, object] | None = None):
        super().__init__(message)
        self.reason = reason
        self.context = context or {}


def validate_and_prepare_trade(
    incoming: TradeRequest,
    current: TradeResponse | None,
    *,
    today: date | None = None,
) -> TradeResponse:
    effective_today = today or date.today()

    if incoming.maturity_date < effective_today:
        raise TradeValidationError(
            "maturity date cannot be before today",
            reason="maturity_before_today",
            context={
                "incoming_maturity_date": incoming.maturity_date,
                "today": effective_today,
            },
        )

    if current is not None and incoming.version < current.version:
        raise TradeValidationError(
            "incoming version is lower than current version",
            reason="incoming_version_lower",
            context={
                "incoming_version": incoming.version,
                "current_version": current.version,
            },
        )

    return TradeResponse(
        trade_id=incoming.trade_id,
        version=incoming.version,
        counterparty_id=incoming.counterparty_id,
        book_id=incoming.book_id,
        maturity_date=incoming.maturity_date,
        created_date=effective_today,
    )
