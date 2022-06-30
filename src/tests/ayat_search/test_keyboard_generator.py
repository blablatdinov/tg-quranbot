from aiogram import types

from services.ayat import AyatSearchKeyboard


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
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['3:15']


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
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['2:6,7']


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
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['3:15', '2:6,7']
