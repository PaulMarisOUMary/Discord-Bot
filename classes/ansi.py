from enum import IntEnum

ESCAPE = '\u001b'

def _to_color(*colors_code: str) -> str:
    """Color code to ANSI escape sequence."""
    return f"{ESCAPE}[{';'.join(colors_code)}m"

class StackANSI():
    def __init__(self, num: int):
        self.series = [num]

    def __add__(self, __x: 'SingleANSI') -> 'StackANSI':
        self.series.append(__x.value)
        return self

    def __str__(self) -> str:
        return _to_color(*set([str(x) for x in self.series]))

class SingleANSI(IntEnum):
    def __add__(self, __x: 'SingleANSI') -> int:
        return StackANSI(self.value) + __x

    def __str__(self) -> str:
        return _to_color(str(self.value))

class Format(SingleANSI):
    """Formating codes."""
    RESET = 0
    NORMAL = RESET
    BOLD = 1
    UNDERLINE = 4

class Foreground(SingleANSI):
    """Foreground color codes."""
    GRAY = 30
    GREY = GRAY
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PINK = 35
    CYAN = 36
    WHITE = 37

class Background(SingleANSI):
    """Background color codes."""
    FIREFLY_DARK_BLUE = 40
    ORANGE = 41
    MARBLE_BLUE = 42
    GREYISH_TURQUOISE = 43
    GRAY = 44
    GREY = GRAY
    INDIGO = 45
    LIGHT_GRAY = 46
    LIGHT_GREY = LIGHT_GRAY
    WHITE = 47