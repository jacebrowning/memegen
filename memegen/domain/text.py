class Text:

    def __init__(self, path=None):
        self._parts = [] if path is None else path.split('/')

    def __getitem__(self, key):
        try:
            part = self._parts[key]
        except (IndexError, ValueError):
            return ""
        else:
            return part.strip()

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

        previous_part = True
        for part in self:
            if part:
                line = self._format_line(part)
                lines.append(line)
            elif not previous_part:
                break
            else:
                lines.append('_')
            previous_part = part

        return lines[:-1]

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

        previous_upper = True
        for char in part:
            if char in ('_', '-'):
                chars.append(' ')
            else:
                if char.isupper():
                    if not previous_upper and chars[-1] != ' ':
                        chars.append(' ')

                chars.append(char.upper())
                previous_upper = char.isupper()

        return ''.join(chars)

    @staticmethod
    def _format_path(line):
        if line == ' ':
            return '_'
        else:
            return line.replace(' ', '-').lower()
