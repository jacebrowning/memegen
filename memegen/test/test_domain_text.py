from memegen.domain import Text


class TestText:

    def test_init_none(self):
        text = Text()
        assert "" == text.top
        assert "" == text.bottom

    def test_init_0_slashes(self):
        text = Text("foo")
        assert "FOO" == text.top
        assert "" == text.bottom

    def test_init_1_slash(self):
        text = Text("foo/bar")
        assert "FOO" == text.top
        assert "BAR" == text.bottom
        assert "" == text.get_line(2)

    def test_init_2_slashes(self):
        text = Text("foo/bar/qux")
        assert "FOO" == text.top
        assert "BAR" == text.bottom
        assert "QUX" == text.get_line(2)
        assert "" == text.get_line(3)

    def test_lines_split_underscore_as_spaces(self):
        text = Text("hello_world")
        assert ["HELLO WORLD"] == text.lines

    def test_lines_split_dash_as_spaces(self):
        text = Text("hello-world")
        assert ["HELLO WORLD"] == text.lines

    def test_lines_split_case_as_spaces(self):
        text = Text("helloWorld")
        assert ["HELLO WORLD"] == text.lines

    def test_lines_kepp_spaces(self):
        text = Text("hello world")
        assert ["HELLO WORLD"] == text.lines

    def test_lines_ignore_initial_capital(self):
        text = Text("HelloWorld")
        assert ["HELLO WORLD"] == text.lines

    def test_lines_ignore_capital_after_sep(self):
        text = Text("hello-World")
        assert ["HELLO WORLD"] == text.lines

    def test_path(self):
        text = Text("hello/World")
        assert "hello/world" == text.path

    def test_path_with_dashes(self):
        text = Text("with-dashes/in-it")
        assert "with-dashes/in-it" == text.path

    def test_path_with_underscores(self):
        text = Text("with_underscores/in_it")
        assert "with-underscores/in-it" == text.path

    def test_path_with_case_changes(self):
        text = Text("withCaseChanges/InIT")
        assert "with-case-changes/in-it" == text.path
