from dataclasses import dataclass

import pytest

from exceptions.content_exceptions import UserHasNotFavoriteAyatsError
from repository.ayats.ayat import Ayat
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from services.ayats.ayat_search import FavoriteAyats
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from tests.ayat_search.test_keyboard_generator import FavoriteAyatsRepositoryMock
from tests.mocks.ayat_repository import AyatRepositoryMock


@dataclass
class UserMock(object):
    chat_id: int
    favorite_ayat_ids: list[int]


class LocalAyatRepositoryMock(FavoriteAyatRepositoryInterface):

    _ayats: list[Ayat]
    _users: list[UserMock]

    def __init__(self, ayats, user_mocks: list[UserMock]):
        self._ayats = ayats
        self._users = user_mocks

    async def add_to_favorite(self, chat_id: int, ayat_id: int):
        user = list(
            filter(
                lambda user: user.chat_id == chat_id,
                self._users,
            ),
        )[0]
        user.favorite_ayat_ids.append(ayat_id)

    async def get_favorites(self, chat_id: int):
        user = [user for user in self._users if user.chat_id == chat_id][0]
        return [
            ayat
            for ayat in self._ayats
            if ayat.id in user.favorite_ayat_ids
        ]

    async def remove_from_favorite(self, chat_id: int, ayat_id: int):
        user = list(
            filter(
                lambda user: user.chat_id == chat_id,
                self._users,
            ),
        )[0]
        user.favorite_ayat_ids.remove(ayat_id)

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        user = list(
            filter(
                lambda user: user.chat_id == chat_id,
                self._users,
            ),
        )[0]
        return ayat_id in user.favorite_ayat_ids


@pytest.fixture()
def ayat_repository_mock_with_none_favorites(ayat_factory):
    return LocalAyatRepositoryMock(
        [ayat_factory(1, '1:1-7'), ayat_factory(2, '2:1-5')],
        [UserMock(chat_id=123, favorite_ayat_ids=[])],
    )


@pytest.fixture()
def ayat_repository_mock_with_one_favorite(ayat_factory):
    return LocalAyatRepositoryMock(
        [ayat_factory(1, '1:1-7'), ayat_factory(2, '2:1-5')],
        [UserMock(chat_id=123, favorite_ayat_ids=[1])],
    )


async def test_none_favorites(ayat_repository_mock_with_none_favorites):
    with pytest.raises(UserHasNotFavoriteAyatsError):
        await FavoriteAyats(
            ayat_repository_mock_with_none_favorites,
            123,
        ).search()


class AyatSearchMock(AyatSearchInterface):

    def __init__(self, ayat_repository: AyatRepositoryMock):
        self.ayat_repository = ayat_repository

    async def search(self) -> Ayat:
        return self.ayat_repository.storage[1]


async def test_one_favorite(ayat_repository_mock_with_one_favorite, ayat_repository_mock):
    got = await AyatSearchKeyboard(
        AyatSearchMock(ayat_repository_mock),
        FavoriteAyatsRepositoryMock(),
        21442,
        AyatPaginatorCallbackDataTemplate.favorite_ayat_template,
    ).generate()

    assert got.to_python() == {
        "inline_keyboard": [
            [
                {"text": "Добавить в избранное", "callback_data": "add_to_favorite(2)"},
            ],
        ],
    }

