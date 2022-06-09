from enum import IntEnum
from typing import Any

ESCAPE: str = '\u001b'

class ANSI(IntEnum):

    def _to_color(self, *colors_code: str) -> str:
        return f"{ESCAPE}[{';'.join(colors_code)}m"

    def __call__(self) -> str:
        return self._to_color(str(self))

    def __str__(self) -> str:
        return str(self.value)

    def __add__(self, __x: Any) -> str:
        if isinstance(self, (Background, Format, Foreground)):
            print(self.value, type(self.value))
        print(f"{type(self)} + {type(__x)}")
        return self._to_color(str(self), str(__x))

class Format(ANSI):
    RESET = 0
    NORMAL = RESET
    BOLD = 1
    UNDERLINE = 4

class Foreground(ANSI):
    GRAY = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PINK = 35
    CYAN = 36
    WHITE = 37

class Background(ANSI):
    FIREFLY_DARK_BLUE = 40
    ORANGE = 41
    MARBLE_BLUE = 42
    GREYISH_TURQUOISE = 43
    GRAY = 44
    INDIGO = 45
    LIGHT_GRAY = 46
    WHITE = 47

a = Format.RESET
b = Background.GRAY
c = Foreground.BLUE

# print(type(a), a)
# print(type(b), b)
# print(type(c), c)
#print(type(a + b))
print(a+b)
print(a + b + c)