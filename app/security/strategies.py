from abc import ABC, abstractmethod

from app.security.models import Principal


class AuthenticationStrategy(ABC):
    @abstractmethod
    def authenticate(self, bearer_token: str | None, user_header: str | None) -> Principal:
        raise NotImplementedError


class AuthorizationStrategy(ABC):
    @abstractmethod
    def can_write_trade(self, principal: Principal) -> bool:
        raise NotImplementedError

    @abstractmethod
    def can_read_trade(self, principal: Principal) -> bool:
        raise NotImplementedError


class PlaceholderAuthenticationStrategy(AuthenticationStrategy):
    def authenticate(self, bearer_token: str | None, user_header: str | None) -> Principal:
        user_id = user_header or "anonymous"
        is_authenticated = bool(bearer_token or user_header)
        return Principal(user_id=user_id, scopes=set(), is_authenticated=is_authenticated)


class AllowAllAuthorizationStrategy(AuthorizationStrategy):
    def can_write_trade(self, principal: Principal) -> bool:
        return True

    def can_read_trade(self, principal: Principal) -> bool:
        return True
