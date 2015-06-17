class Text:

    def __init__(self, lines=None):
        self._lines = lines or []

    @property
    def top(self):
        try:
            return self._lines[0]
        except IndexError:
            return ""

    @property
    def bottom(self):
        try:
            return self._lines[1]
        except IndexError:
            return ""
