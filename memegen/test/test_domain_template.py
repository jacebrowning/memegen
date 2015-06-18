from unittest.mock import patch, Mock

from memegen.domain import Template


class TestTemplate:

    def test_comparison(self):
        t1 = Template('abc', "A Thing")
        t2 = Template('def')
        t3 = Template('def', "Do This")
        assert t1 != t2
        assert t2 == t3
        assert t1 < t3

    def test_path(self):
        template = Template('abc', root="my_root")
        with patch('os.path.isfile', Mock(return_value=True)):
            path = template.path
        assert "my_root/abc/default.png" == path

    def test_path_none(self):
        template = Template('abc', root="my_root")
        with patch('os.path.isfile', Mock(return_value=False)):
            path = template.path
        assert path is None
