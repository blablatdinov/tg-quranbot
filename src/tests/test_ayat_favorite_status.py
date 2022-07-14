from dataclasses import dataclass

import pytest

from app_types.intable import Intable
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from services.ayats.ayat_search import AyatFavoriteStatus


@dataclass
class UserMock(object):
    chat_id: int
    favorite_ayat_ids: list[int]


class AyatRepositoryMock(AyatRepositoryInterface):

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
            )
        )[0]
        user.favorite_ayat_ids.append(ayat_id)

    async def remove_from_favorite(self, chat_id: int, ayat_id: int):
        user = list(
            filter(
                lambda user: user.chat_id == chat_id,
                self._users,
            )
        )[0]
        user.favorite_ayat_ids.remove(ayat_id)

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        user = list(
            filter(
                lambda user: user.chat_id == chat_id,
                self._users,
            )
        )[0]
        return ayat_id in user.favorite_ayat_ids


@pytest.fixture()
def ayat_repository_mock(ayat_factory):
    return AyatRepositoryMock(
        [ayat_factory(1, '1:1-7'), ayat_factory(2, '2:1-5')],
        [UserMock(chat_id=123, favorite_ayat_ids=[1])]
    )


async def test_change_to_favorite(ayat_repository_mock):
    await AyatFavoriteStatus(
        ayat_repository_mock,
        2,
        123
    ).change(True)

    assert await ayat_repository_mock.check_ayat_is_favorite_for_user(2, 123)


async def test_change_to_not_favorite(ayat_repository_mock):
    await AyatFavoriteStatus(
        ayat_repository_mock,
        1,
        123
    ).change(False)

    assert not await ayat_repository_mock.check_ayat_is_favorite_for_user(2, 123)
