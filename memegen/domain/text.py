class Text:

    def __init__(self, path=None):
        self._parts = [] if path is None else path.split('/')

    def __getitem__(self, key):
        try:
            part = self._parts[key]
        except (IndexError, ValueError):
            return ""
        else:
            return part

    def get_line(self, index):
        return self._format_line(self[index])

    @property
    def top(self):
        return self.get_line(0)

    @property
    def bottom(self):
        return self.get_line(1)

    @property
    def lines(self):
        lines = []

        for part in self:
            if part:
                line = self._format_line(part)
                lines.append(line)
            else:
                break

        return lines

    @property
    def path(self):
        paths = []

        for line in self.lines:
            path = self._format_path(line)
            paths.append(path)

        return '/'.join(paths)

    @staticmethod
    def _format_line(part):
        chars = []

        upper = True
        for char in part:
            if char in ('_', '-'):
                chars.append(' ')
                upper = True
            else:
                if char.isupper():
                    if not upper:
                        chars.append(' ')
                chars.append(char.upper())
                upper = char.isupper()

        return ''.join(chars)

    @staticmethod
    def _format_path(line):
        return line.replace(' ', '-').lower()
