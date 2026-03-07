from dataclasses import dataclass, field


@dataclass(slots=True)
class Principal:
    user_id: str
    scopes: set[str] = field(default_factory=set)
    is_authenticated: bool = False
