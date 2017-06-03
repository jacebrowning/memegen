class Text:

    EMPTY = '_'
    SPACE = '_'
    ALTERNATE_SPACES = ['_', '-']
    SPECIAL_CHARACTERS = {
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
        return bool(self.path.strip(self.SPACE + '/'))

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
    def _format_line(cls, text, translate_spaces):
        for special, replacement in cls.SPECIAL_CHARACTERS.items():
            text = text.replace(replacement, special)
            text = text.replace(replacement.upper(), special)

        chars = []
        escape = None

        for index, char in enumerate(text):

            if char in cls.ALTERNATE_SPACES and translate_spaces:
                if char == escape:
                    chars[-1] = escape
                    escape = None
                else:
                    chars.append(' ')
                    escape = char
                continue
            else:
                escape = None

            if not char.isalpha():
                chars.append(char)
                continue

            if len(chars) >= 2:
                if char.isupper() and chars[-1].islower() and chars[-2] != ' ':
                    chars.append(' ' + char)
                    continue

            if len(chars) >= 1 and len(text) > index + 1:
                n_char = text[index + 1]
                if char.isupper() and chars[-1].isupper() and n_char.islower():
                    chars.append(' ' + char)
                    continue

            chars.append(char)

        return ''.join(chars).upper()

    @classmethod
    def _format_path(cls, line):
        if line == ' ':
            path = cls.EMPTY
        else:
            path = line.lower()
            for space in cls.ALTERNATE_SPACES:
                path = path.replace(space, space * 2)
            path = path.replace(' ', cls.SPACE)
            for special, replacement in cls.SPECIAL_CHARACTERS.items():
                path = path.replace(special, replacement)

        return path

    def get_line(self, index):
        return self._format_line(self[index], self._translate_spaces)
