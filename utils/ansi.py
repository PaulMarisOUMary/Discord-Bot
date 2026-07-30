from __future__ import annotations

from enum import Enum

ESCAPE = '\u001b'


class BaseANSI:
    @property
    def codes(self) -> tuple[int, ...]:
        raise NotImplementedError

    def __add__(self, other: BaseANSI) -> StackANSI:
        if isinstance(other, BaseANSI):
            return StackANSI(*self.codes, *other.codes)
        raise NotImplementedError

    def __str__(self) -> str:
        unique_codes = dict.fromkeys(str(c) for c in self.codes)
        return f"{ESCAPE}[{';'.join(unique_codes)}m"


class StackANSI(BaseANSI):
    def __init__(self, *codes: int) -> None:
        self._codes = codes

    @property
    def codes(self) -> tuple[int, ...]:
        return self._codes


class SingleANSI(BaseANSI, Enum):
    value: int

    @property
    def codes(self) -> tuple[int, ...]:
        return (self.value,)


class Format(SingleANSI):
    """Formating codes."""

    RESET = 0
    NORMAL = RESET
    BOLD = 1
    UNDERLINE = 4


class Foreground(SingleANSI):
    """Foreground color codes."""

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PINK = 35
    CYAN = 36
    WHITE = 37


class Background(SingleANSI):
    """Background color codes."""

    BLACK = 40
    ORANGE = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    PINK = 45
    CYAN = 46
    WHITE = 47
