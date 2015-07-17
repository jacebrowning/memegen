# pylint: disable=R,C

from memegen.domain import Text


class TestTextInit:

    def test_none(self):
        text = Text()
        assert "" == text.top
        assert "" == text.bottom

    def test_0_slashes(self):
        text = Text("foo")
        assert "FOO" == text.top
        assert "" == text.bottom

    def test_1_slash(self):
        text = Text("foo/bar")
        assert "FOO" == text.top
        assert "BAR" == text.bottom
        assert "" == text.get_line(2)

    def test_2_slashes(self):
        text = Text("foo/bar/qux")
        assert "FOO" == text.top
        assert "BAR" == text.bottom
        assert "QUX" == text.get_line(2)
        assert "" == text.get_line(3)


class TestTextLines:

    def test_split_underscore_as_spaces(self):
        text = Text("hello_world")
        assert ["HELLO WORLD"] == text.lines

    def test_split_dash_as_spaces(self):
        text = Text("hello-world")
        assert ["HELLO WORLD"] == text.lines

    def test_split_case_as_spaces(self):
        text = Text("helloWorld")
        assert ["HELLO WORLD"] == text.lines

    def test_keep_spaces(self):
        text = Text("hello world")
        assert ["HELLO WORLD"] == text.lines

    def test_case_ignored_after_space(self):
        text = Text("HELLO WORLD")
        assert ["HELLO WORLD"] == text.lines

    def test_ignore_initial_capital(self):
        text = Text("HelloWorld")
        assert ["HELLO WORLD"] == text.lines

    def test_ignore_capital_after_sep(self):
        text = Text("hello-World")
        assert ["HELLO WORLD"] == text.lines

    def test_strip_spaces(self):
        text = Text("  hello  World /    ")
        assert ["HELLO  WORLD"] == text.lines

    def test_duplicate_capitals_treated_as_spaces(self):
        text = Text("IWantTHISPattern_to-Work")
        assert ["I WANT THIS PATTERN TO WORK"] == text.lines

    def test_no_space_after_apostrophe(self):
        text = Text("that'd be great")
        assert ["THAT'D BE GREAT"] == text.lines

    def test_double_dashes_are_escaped(self):
        text = Text("i'm----  /working 9--5")
        assert ["I'M--", "WORKING 9-5"] == text.lines

    def test_double_underscores_are_escaped(self):
        text = Text("Calls ____init____/with __args")
        assert ["CALLS __INIT__", "WITH _ARGS"] == text.lines

    def test_special_characters_are_kept(self):
        text = Text("special!?")
        assert ["SPECIAL!?"] == text.lines

    def test_escaped_characters_are_converted(self):
        text = Text("special~q~Q~E~e")
        assert ["SPECIAL??!!"] == text.lines


class TestTextPath:

    def test_case_ignored(self):
        text = Text("hello/World")
        assert "hello/world" == text.path

    def test_single_dashes_kept(self):
        text = Text("with-dashes/in-it")
        assert "with-dashes/in-it" == text.path

    def test_underscores_become_dashes(self):
        text = Text("with_underscores/in_it")
        assert "with-underscores/in-it" == text.path

    def test_case_changes_become_dashes(self):
        text = Text("withCaseChanges/InIT")
        assert "with-case-changes/in-it" == text.path

    def test_extra_spaces_are_stripped(self):
        text = Text("  with  spaces/  in it   / ")
        assert "with--spaces/in-it" == text.path

    def test_single_underscore_is_kept(self):
        text = Text(" _     ")
        assert "_" == text.path

    def test_duplicate_capitals_are_ignored(self):
        text = Text("IWantTHISPattern_to-Work")
        assert "i-want-this-pattern-to-work" == text.path

    def test_double_dashes_are_escaped(self):
        text = Text("i'm----  /working 9--5")
        assert "i'm----/working-9--5" == text.path

    def test_double_underscores_are_escaped(self):
        text = Text("Calls ____init____/with __args")
        assert "calls-____init____/with-__args" == text.path

    def test_special_characters_are_escaped(self):
        text = Text("special!?")
        assert "special~e~q" == text.path
