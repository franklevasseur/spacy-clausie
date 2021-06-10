

class StartEnd:

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def includes(self, cursor: int, includeBorders=False):
        if (includeBorders):
            return self.start <= cursor and self.end >= cursor

        return self.start < cursor and self.end > cursor

    def intersects(self, other):
        return (self.includes(other.start)
                or self.includes(other.end)
                or other.includes(self.start)
                or other.includes(self.end)
                )
