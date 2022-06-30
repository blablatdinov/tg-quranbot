import re

import pytest
from aiogram import types

from constants import AYAT_SEARCH_INPUT_REGEXP
from repository.ayats import Ayat
from services.ayat import AyatsService, AyatSearchKeyboard
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
        'arab_text': fake_text(),
        'content': fake_text(),
        'transliteration': fake_text(),
        'sura_link': fake_text(),
        'audio_telegram_id': fake_text(),
        'link_to_audio_file': fake_text(),
    }
    mock.storage = [
        Ayat(id=1, sura_num=1, ayat_num='1-7', **common_params),
        Ayat(id=2, sura_num=3, ayat_num='15', **common_params),
        Ayat(id=3, sura_num=2, ayat_num='10', **common_params),
        Ayat(id=4, sura_num=2, ayat_num='6,7', **common_params),
        Ayat(id=5737, sura_num=114, ayat_num='1-4', **common_params),
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


async def test_keyboard_for_first_ayat(ayat_repository_mock):
    got = await AyatSearchKeyboard(
        ayat_repository_mock,
        ayat_repository_mock.storage[0],
        21442,
    ).generate()
    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [x['text'] for x in keyboard_first_row] == ['3:15']


async def test_keyboard_for_last_ayat(ayat_repository_mock):
    got = await AyatSearchKeyboard(
        ayat_repository_mock,
        ayat_repository_mock.storage[-1],
        21442,
    ).generate()
    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [x['text'] for x in keyboard_first_row] == ['2:6,7']


async def test_keyboard_for_middle_ayat(ayat_repository_mock):
    got = await AyatSearchKeyboard(
        ayat_repository_mock,
        ayat_repository_mock.storage[2],
        21442,
    ).generate()

    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [x['text'] for x in keyboard_first_row] == ['3:15', '2:6,7']
