from memegen.domain import Text


class TestText:

    def test_init_with_none(self):
        text = Text()
        assert "" == text.top
        assert "" == text.bottom

    def test_init_with_1(self):
        text = Text(["foo"])
        assert "foo" == text.top
        assert "" == text.bottom

    def test_init_with_2(self):
        text = Text(["foo", "bar"])
        assert "foo" == text.top
        assert "bar" == text.bottom

    def test_init_with_3(self):
        text = Text(["foo", "bar", "qux"])
        assert "foo" == text.top
        assert "bar" == text.bottom
