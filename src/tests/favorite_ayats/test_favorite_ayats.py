import pytest

from exceptions.content_exceptions import UserHasNotFavoriteAyatsError
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from repository.ayats.schemas import Ayat, AyatShort
from services.ayats.ayat_search import FavoriteAyats
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from tests.ayat_search.test_keyboard_generator import FavoriteAyatsRepositoryMock
from tests.mocks.ayat_repository import AyatRepositoryMock


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
        'inline_keyboard': [
            [
                {'text': 'Добавить в избранное', 'callback_data': 'add_to_favorite(2)'},
            ],
        ],
    }


class FavoriteAyatsMock(AyatSearchInterface):

    def __init__(self, return_value: Ayat):
        self._return_value = return_value

    async def search(self) -> Ayat:
        return self._return_value


class NeighborAyatsRepositoryMock(NeighborAyatsRepositoryInterface):

    def __init__(self, return_value: list[AyatShort]):
        self._return_value = return_value

    async def get_ayat_neighbors(self, ayat_id: int) -> list[AyatShort]:
        return self._return_value


async def test_two_favorites(ayat_factory, ayat_repository_mock_with_two_favorite, ayat_repository_mock):
    got = await AyatSearchWithNeighbors(
        FavoriteAyatsMock(ayat_factory(2, '1:1-7')),
        NeighborAyatsRepositoryMock([
            AyatShort(
                id=2,
                sura_num=1,
                ayat_num='1-7',
            ),
            AyatShort(
                id=3,
                sura_num=2,
                ayat_num='1-5',
            ),
        ]),
    ).search()

    assert got.left_neighbor is None
    assert got.right_neighbor is not None
