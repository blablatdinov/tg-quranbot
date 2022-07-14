import pytest

from exceptions import BaseAppError
from services.regular_expression import IntableRegularExpression


@pytest.mark.parametrize('input_,expected', [
    ('6598Ijowe1234', 6598),
    ('some56text', 56),
])
def test(input_, expected):
    got = int(IntableRegularExpression(r'\d+', input_))

    assert got == expected


def test_invalid():
    with pytest.raises(BaseAppError):
        int(IntableRegularExpression(r'\d+', 'without numbers'))
