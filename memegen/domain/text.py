class Text:

    EMPTY = '_'
    SPACE = '-'
    SPECIAL = {
        '?': '~q',
        '%': '~p',
        '#': '~h',
        '/': '~s',
        '"': "''",
    }

    def __init__(self, path=None, *, translate_spaces=True):
        if path is None:
            self._parts = []
        elif isinstance(path, str):
            self._parts = path.split('/')
        else:
            assert isinstance(path, list)
            self._parts = path
        self._translate_spaces = translate_spaces

    def __str__(self):
        return ' / '.join(self.lines)

    def __bool__(self):
        return bool(self.path.strip(self.EMPTY + '/'))

    def __getitem__(self, key):
        try:
            part = self._parts[key]
        except (IndexError, ValueError):
            return ""
        else:
            return part.strip()

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
                line = self._format_line(part, self._translate_spaces)
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

    @classmethod
    def _format_line(cls, part, translate_spaces):
        for special, replacement in cls.SPECIAL.items():
            part = part.replace(replacement, special)
            part = part.replace(replacement.upper(), special)

        part = list(part)
        chars = []

        previous_upper = True
        previous_char = None
        for i, char in enumerate(part):
            if translate_spaces and char in (cls.EMPTY, cls.SPACE):
                if char == previous_char:
                    chars[-1] = char
                    previous_char = None
                    continue
                else:
                    chars.append(' ')
            elif not char.isalpha():
                chars.append(char)
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

    @classmethod
    def _format_path(cls, line):
        if line == ' ':
            path = cls.EMPTY
        else:
            path = line.lower()
            path = path.replace(cls.SPACE, cls.SPACE * 2)
            path = path.replace(cls.EMPTY, cls.EMPTY * 2)
            path = path.replace(' ', cls.SPACE)
            for special, replacement in cls.SPECIAL.items():
                path = path.replace(special, replacement)

        return path

    def get_line(self, index):
        return self._format_line(self[index], self._translate_spaces)
