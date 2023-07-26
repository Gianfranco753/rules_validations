from typing import TypedDict, Callable


class Rule(TypedDict):
    active: bool
    path: str
    test: Callable
    msg: str
