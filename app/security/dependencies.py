from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.models import Principal
from app.security.strategies import (
    AllowAllAuthorizationStrategy,
    PlaceholderAuthenticationStrategy,
)


bearer_scheme = HTTPBearer(auto_error=False)
authn_strategy = PlaceholderAuthenticationStrategy()
authz_strategy = AllowAllAuthorizationStrategy()


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> Principal:
    token = credentials.credentials if credentials else None
    return authn_strategy.authenticate(bearer_token=token, user_header=x_user_id)


def require_trade_write(principal: Principal = Depends(get_current_principal)) -> Principal:
    if not authz_strategy.can_write_trade(principal):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return principal


def require_trade_read(principal: Principal = Depends(get_current_principal)) -> Principal:
    if not authz_strategy.can_read_trade(principal):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return principal
