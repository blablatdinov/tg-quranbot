from aiogram import types

from services.ayat import AyatSearchKeyboard
from tests.mocks import NeighborAyatsRepositoryMock


async def test_keyboard_for_first_ayat(ayat_repository_mock):
    ayat = ayat_repository_mock.storage[0]
    got = AyatSearchKeyboard(
        ayat_repository=ayat_repository_mock,
        ayat_id=ayat.id,
        ayat_is_favorite=True,
        ayat_neighbors=await NeighborAyatsRepositoryMock(ayat_repository_mock.storage).get_ayat_neighbors(ayat.id),
        chat_id=21442,
    ).generate()
    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['3:15']
    assert [keyboard_button['callback_data'] for keyboard_button in keyboard_first_row] == ['get_ayat(2)']


async def test_keyboard_for_last_ayat(ayat_repository_mock):
    ayat = ayat_repository_mock.storage[-1]
    got = AyatSearchKeyboard(
        ayat_repository=ayat_repository_mock,
        ayat_id=ayat.id,
        ayat_is_favorite=True,
        ayat_neighbors=await NeighborAyatsRepositoryMock(ayat_repository_mock.storage).get_ayat_neighbors(ayat.id),
        chat_id=21442,
    ).generate()
    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['2:6,7']
    assert [keyboard_button['callback_data'] for keyboard_button in keyboard_first_row] == ['get_ayat(4)']


async def test_keyboard_for_middle_ayat(ayat_repository_mock):
    ayat = ayat_repository_mock.storage[2]
    got = AyatSearchKeyboard(
        ayat_repository=ayat_repository_mock,
        ayat_id=ayat.id,
        ayat_is_favorite=True,
        ayat_neighbors=await NeighborAyatsRepositoryMock(ayat_repository_mock.storage).get_ayat_neighbors(ayat.id),
        chat_id=21442,
    ).generate()

    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['3:15', '2:6,7']
    assert (
        [keyboard_button['callback_data'] for keyboard_button in keyboard_first_row]
        == ['get_ayat(2)', 'get_ayat(4)']
    )


async def test_add_to_favorite(ayat_repository_mock):
    ayat = ayat_repository_mock.storage[2]
    got = AyatSearchKeyboard(
        ayat_repository=ayat_repository_mock,
        ayat_id=ayat.id,
        ayat_is_favorite=False,
        ayat_neighbors=await NeighborAyatsRepositoryMock(ayat_repository_mock.storage).get_ayat_neighbors(ayat.id),
        chat_id=21442,
    ).generate()

    add_to_favorite_button = dict(got)['inline_keyboard'][-1][0]

    assert add_to_favorite_button['callback_data'] == 'add_to_favorite(3)'
    assert add_to_favorite_button['text'] == 'Добавить в избранное'


async def test_remove_from_favorite(ayat_repository_mock):
    ayat = ayat_repository_mock.storage[0]
    got = AyatSearchKeyboard(
        ayat_repository=ayat_repository_mock,
        ayat_id=ayat.id,
        ayat_is_favorite=True,
        ayat_neighbors=await NeighborAyatsRepositoryMock(ayat_repository_mock.storage).get_ayat_neighbors(ayat.id),
        chat_id=21442,
    ).generate()

    add_to_favorite_button = dict(got)['inline_keyboard'][-1][0]

    assert add_to_favorite_button['callback_data'] == 'remove_from_favorite(1)'
    assert add_to_favorite_button['text'] == 'Удалить из избранного'
