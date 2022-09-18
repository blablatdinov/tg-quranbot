from dataclasses import dataclass

from aiogram import types

from repository.ayats.schemas import Ayat
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from services.ayats.ayat_search import AyatPaginatorCallbackDataTemplate
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.keyboard import AyatSearchKeyboard
from tests.mocks.ayat_repository import AyatRepositoryMock


@dataclass
class AyatSearchFake(AyatSearchInterface):

    ayat_repository: AyatRepositoryMock
    search_input: str

    async def search(self) -> Ayat:
        ayat = list(
            filter(
                lambda ayat: ayat.title() == self.search_input,
                self.ayat_repository.storage,
            ),
        )[0]
        if self._is_last_ayat(ayat.id):
            ayat.left_neighbor = (await self.ayat_repository.get(ayat.id - 1)).get_short()
        elif self._is_first_ayat(ayat.id):
            ayat.right_neighbor = (await self.ayat_repository.get(ayat.id + 1)).get_short()
        else:
            ayat.left_neighbor = (await self.ayat_repository.get(ayat.id - 1)).get_short()
            ayat.right_neighbor = (await self.ayat_repository.get(ayat.id + 1)).get_short()
        return ayat

    def _is_last_ayat(self, ayat_id) -> bool:
        return self.ayat_repository.storage[-1].id == ayat_id

    def _is_first_ayat(self, ayat_id) -> bool:
        return self.ayat_repository.storage[0].id == ayat_id


class FavoriteAyatsRepositoryMock(FavoriteAyatRepositoryInterface):

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        return ayat_id == 1 and chat_id == 21442


async def test_keyboard_for_first_ayat(ayat_repository_mock):
    search_input = ayat_repository_mock.storage[0].title()
    got = await AyatSearchKeyboard(
        ayat_search=AyatSearchFake(ayat_repository_mock, search_input),
        favorite_ayats_repository=FavoriteAyatsRepositoryMock(),
        chat_id=21442,
        pagination_buttons_keyboard=AyatPaginatorCallbackDataTemplate.ayat_search_template,
    ).generate()
    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['3:15 ➡️']
    assert [keyboard_button['callback_data'] for keyboard_button in keyboard_first_row] == ['get_ayat(2)']


async def test_keyboard_for_last_ayat(ayat_repository_mock):
    search_ayat = ayat_repository_mock.storage[-1].title()
    got = await AyatSearchKeyboard(
        ayat_search=AyatSearchFake(ayat_repository_mock, search_ayat),
        favorite_ayats_repository=FavoriteAyatsRepositoryMock(),
        chat_id=21442,
        pagination_buttons_keyboard=AyatPaginatorCallbackDataTemplate.ayat_search_template,
    ).generate()
    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['⬅️ 113:1-6']
    assert [keyboard_button['callback_data'] for keyboard_button in keyboard_first_row] == ['get_ayat(5736)']


async def test_keyboard_for_middle_ayat(ayat_repository_mock):
    search_input = ayat_repository_mock.storage[2].title()
    got = await AyatSearchKeyboard(
        ayat_search=AyatSearchFake(ayat_repository_mock, search_input),
        favorite_ayats_repository=FavoriteAyatsRepositoryMock(),
        chat_id=21442,
        pagination_buttons_keyboard=AyatPaginatorCallbackDataTemplate.ayat_search_template,
    ).generate()

    keyboard_as_list = dict(got)['inline_keyboard']
    keyboard_first_row = keyboard_as_list[0]

    assert isinstance(got, types.InlineKeyboardMarkup)
    assert len(keyboard_as_list) == 2
    assert [keyboard_button['text'] for keyboard_button in keyboard_first_row] == ['⬅️ 3:15', '2:6,7 ➡️']
    assert (
        [keyboard_button['callback_data'] for keyboard_button in keyboard_first_row]
        == ['get_ayat(2)', 'get_ayat(4)']
    )


async def test_add_to_favorite(ayat_repository_mock):
    search_input = ayat_repository_mock.storage[2].title()
    got = await AyatSearchKeyboard(
        ayat_search=AyatSearchFake(ayat_repository_mock, search_input),
        favorite_ayats_repository=FavoriteAyatsRepositoryMock(),
        chat_id=21442,
        pagination_buttons_keyboard=AyatPaginatorCallbackDataTemplate.ayat_search_template,
    ).generate()

    add_to_favorite_button = dict(got)['inline_keyboard'][-1][0]

    assert add_to_favorite_button['callback_data'] == 'add_to_favorite(3)'
    assert add_to_favorite_button['text'] == 'Добавить в избранное'


async def test_remove_from_favorite(ayat_repository_mock):
    search_input = ayat_repository_mock.storage[0].title()
    got = await AyatSearchKeyboard(
        ayat_search=AyatSearchFake(ayat_repository_mock, search_input),
        favorite_ayats_repository=FavoriteAyatsRepositoryMock(),
        chat_id=21442,
        pagination_buttons_keyboard=AyatPaginatorCallbackDataTemplate.ayat_search_template,
    ).generate()

    add_to_favorite_button = dict(got)['inline_keyboard'][-1][0]

    assert add_to_favorite_button['callback_data'] == 'remove_from_favorite(1)'
    assert add_to_favorite_button['text'] == 'Удалить из избранного'
