import pytest

from services.regular_expression import IntableRegularExpression


@pytest.mark.parametrize('input_,expected', [
    ('8923749', 8923749),
    ('around483759text', 483759),
    ('5347split832457', 5347),
])
def test(input_, expected):
    got = IntableRegularExpression(input_)

    assert int(got) == expected
