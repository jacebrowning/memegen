class Text:

    def __init__(self, path=None):
        self._parts = [] if path is None else path.split('/')

    def __str__(self):
        return ' / '.join(self.lines)

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
                lines.append(' ')
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
        part = list(part)
        chars = []

        previous_upper = True
        previous_char = None
        for i, char in enumerate(part):
            if char in ('_', '-'):
                if char == previous_char:
                    chars[-1] = char
                    previous_char = None
                    continue
                else:
                    chars.append(' ')
            else:
                if char.isupper():
                    if not previous_upper and chars[-1] != ' ':
                        chars.append(' ')
                    else:
                        letters_to_check = part[max(i - 1, 0):i + 2]

                        if len(letters_to_check) == 3:
                            if all((letters_to_check[0].isupper(),
                                    letters_to_check[1].isupper(),
                                    letters_to_check[2].islower())):
                                chars.append(' ')

                chars.append(char.upper())
                previous_upper = char.isupper()
            previous_char = char

        return ''.join(chars)

    @staticmethod
    def _format_path(line):
        if line == ' ':
            return '_'
        else:
            line = line.replace('-', '--').replace('_', '__')
            line = line.replace(' ', '-')
            return line.lower()
