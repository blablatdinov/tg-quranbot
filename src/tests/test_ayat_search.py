import re

import pytest

from constants import AYAT_SEARCH_INPUT_REGEXP
from repository.ayats import Ayat
from services.ayat import AyatsService
from tests.mocks import AyatRepositoryMock


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


@pytest.fixture()
def ayat_repository_mock(fake_text):
    mock = AyatRepositoryMock()
    common_params = {
        'id': 1,
        'arab_text': fake_text(),
        'content': fake_text(),
        'transliteration': fake_text(),
        'sura_link': fake_text(),
        'audio_telegram_id': fake_text(),
        'link_to_audio_file': fake_text(),
    }
    mock.storage = [
        Ayat(sura_num=2, ayat_num='10', **common_params),
        Ayat(sura_num=3, ayat_num='15', **common_params),
        Ayat(sura_num=1, ayat_num='1-7', **common_params),
        Ayat(sura_num=2, ayat_num='6,7', **common_params),
    ]
    return mock


@pytest.mark.parametrize('input_,expect', [
    ('1:1', '1:1-7'),
    ('1:3', '1:1-7'),
    ('1:7', '1:1-7'),
    ('2:10', '2:10'),
    ('3:15', '3:15'),
    ('2:6', '2:6,7'),
    ('2:7', '2:6,7'),
])
@pytest.mark.asyncio
async def test(ayat_repository_mock, input_, expect):
    got = await AyatsService(
        ayat_repository_mock,
        chat_id=123,
    ).search_by_number(input_)

    assert expect in got[0].message


@pytest.mark.parametrize('sura_num', ['0', '115', '-59'])
@pytest.mark.asyncio
async def test_not_found_sura(sura_num):
    got = await AyatsService(
        AyatRepositoryMock(),
        chat_id=123,
    ).search_by_number(f'{sura_num}:1')

    assert got.message == 'Сура не найдена'


@pytest.mark.parametrize('input_', [
    '1:8',
    '2:30',
    '3:-7',
])
@pytest.mark.asyncio
async def test_not_found_ayat(input_, ayat_repository_mock):
    got = await AyatsService(
        AyatRepositoryMock(),
        chat_id=123,
    ).search_by_number(input_)

    assert got.message == 'Аят не найден'
