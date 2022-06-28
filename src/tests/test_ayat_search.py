import re

import pytest

from constants import AYAT_SEARCH_INPUT_REGEXP
from repository.ayats import Ayat
from services.answer import Answer
from services.ayat import AyatsService
from tests.mocks import AyatRepositoryMock

pytestmark = [pytest.mark.asyncio]


@pytest.mark.parametrize('input_,expect', [
    ('1:1', True),
    ('12:1', True),
    ('12:41', True),
    ('2:41', True),
    (':1', False),
    ('1:', False),
])
def test_regexp(input_, expect):
    got = re.search(AYAT_SEARCH_INPUT_REGEXP, input_)

    assert bool(got) is expect


@pytest.fixture()
def ayat_repository_mock(faker):
    mock = AyatRepositoryMock()
    mock.storage = [
        Ayat(
            sura_num=2,
            ayat_num='10',
            arab_text=faker.text(10),
            content=faker.text(10),
            transliteration=faker.text(10),
            sura_link=faker.text(10),
        ),
    ]
    return mock


@pytest.mark.parametrize('input_,expect', [
    ('2:10', 1),
])
async def test_simple(ayat_repository_mock, input_, expect):
    got = await AyatsService(
        ayat_repository_mock,
    ).search_by_number('2:10')

    assert '2:10' in got.message
