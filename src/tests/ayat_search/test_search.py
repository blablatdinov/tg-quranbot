import re

import pytest

from constants import AYAT_SEARCH_INPUT_REGEXP
from exceptions.content_exceptions import AyatNotFoundError, SuraNotFoundError
from services.ayats.search_by_sura_ayat_num import AyatBySuraAyatNum
from tests.mocks.ayat_repository import AyatRepositoryMock


@pytest.mark.parametrize('input_,expect', [
    ('1:1', True),
    ('12:1', True),
    ('12:41', True),
    ('2:41', True),
    (':1', False),
    ('1:', False),
    ('12: 1', True),
    ('12 : 1', True),
    ('12 :1', True),
])
def test_regexp(input_, expect):
    got = re.search(AYAT_SEARCH_INPUT_REGEXP, input_)

    assert bool(got) is expect


@pytest.mark.parametrize('input_,expect', [
    ('1:1', '1:1-7'),
    ('1:3', '1:1-7'),
    ('1:7', '1:1-7'),
    ('2:10', '2:10'),
    ('3:15', '3:15'),
    ('2:6', '2:6,7'),
    ('2:7', '2:6,7'),
])
async def test(ayat_repository_mock, input_, expect):
    got = await AyatBySuraAyatNum(
        ayat_repository_mock,
        input_,
    ).search()

    assert expect in str(got)


@pytest.mark.parametrize('sura_num', ['0', '115', '-59'])
async def test_not_found_sura(sura_num):
    with pytest.raises(SuraNotFoundError):
        await AyatBySuraAyatNum(
            AyatRepositoryMock(),
            f'{sura_num}:1',
        ).search()


@pytest.mark.parametrize('input_', [
    '1:8',
    '2:30',
    '3:-7',
])
async def test_not_found_ayat(input_, ayat_repository_mock):
    with pytest.raises(AyatNotFoundError):
        await AyatBySuraAyatNum(
            AyatRepositoryMock(),
            input_,
        ).search()
