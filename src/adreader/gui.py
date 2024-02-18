import pyautogui

from adreader.utils import RATIO


class ParsableMixin:

    @classmethod
    def parse(cls, s):
        if s.startswith(f'{cls.__name__}[') and s.endswith(']'):
            parsed = map(int, map(str.strip, s[len(cls.__name__)+1:-1].split(',')))
            return cls(*parsed)


class Point(ParsableMixin):
    __slots__ = ()

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __repr__(self):
        return f'Point[{self.x}, {self.y}]'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Box(ParsableMixin):
    tl: Point = Point(0, 0)
    br: Point = Point(0, 0)

    def __init__(self, *args):
        """Initialise Box.

        If two args are provided we assume they are tl Point and br Point.
        Else we assume they are the 4 coordinates.
        """
        if len(args) == 2:
            self.tl = Point(min(args[0].x, args[1].x), min(args[0].y, args[1].y))
            self.br = Point(max(args[0].x, args[1].x), max(args[0].y, args[1].y))
        else:
            self.__init__(Point(args[0], args[1]), Point(args[2], args[3]))

    def __repr__(self):
        return f'Box[{self.tl.x}, {self.tl.y}, {self.br.x}, {self.br.y}]'

    def __eq__(self, other):
        return self.coords == other.coords

    def __gt__(self, other):
        return self.width * self.height > other.width * other.height

    @property
    def width(self):
        return self.br.x - self.tl.x

    @property
    def height(self):
        return self.br.y - self.tl.y

    @property
    def area(self):
        """Return x, y, width, height"""
        return self.tl.x, self.tl.y, self.br.x - self.tl.x, self.br.y - self.tl.y

    @property
    def coords(self):
        """Return tl.x, tl.y, br.x, br.y"""
        return self.tl.x, self.tl.y, self.br.x, self.br.y

    @property
    def scaled(self):
        """Return a Box scaled by RATIO."""
        return Box(self.tl, Point(self.br.x * RATIO, self.br.y * RATIO))

    def capture(self, loc):
        return pyautogui.screenshot(
            imageFilename=loc,
            region=self.area
        )
