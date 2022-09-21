from repository.ayats.schemas import Ayat
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from tests.mocks.neighbor_ayats_repository import NeighborAyatsRepositoryMock


class AyatSearchMock(AyatSearchInterface):

    def __init__(self, ayat_repository_mock, ayat_id: int):
        self.ayat_repository_mock = ayat_repository_mock
        self.ayat_id = ayat_id

    async def search(self) -> Ayat:
        return [ayat for ayat in self.ayat_repository_mock.storage if ayat.id == self.ayat_id][0]


async def test_search_with_neighbors(ayat_repository_mock):
    ayat_search_mock = AyatSearchMock(ayat_repository_mock, 2)
    target_ayat = await ayat_search_mock.search()

    got = await AyatSearchWithNeighbors(
        ayat_search_mock,
        NeighborAyatsRepositoryMock(ayat_repository_mock.storage),
    ).search()

    assert got.left_neighbor
    assert got.right_neighbor
    assert target_ayat.id not in {got.left_neighbor.id, got.right_neighbor.id}


async def test_search_with_neighbors_for_first_ayat(ayat_repository_mock):
    ayat_search_mock = AyatSearchMock(ayat_repository_mock, 1)

    got = await AyatSearchWithNeighbors(
        ayat_search_mock,
        NeighborAyatsRepositoryMock(ayat_repository_mock.storage),
    ).search()

    assert got.left_neighbor is None
    assert got.right_neighbor


async def test_search_with_neighbors_for_last_ayat(ayat_repository_mock):
    ayat_search_mock = AyatSearchMock(ayat_repository_mock, 5737)

    got = await AyatSearchWithNeighbors(
        ayat_search_mock,
        NeighborAyatsRepositoryMock(ayat_repository_mock.storage),
    ).search()

    assert got.left_neighbor
    assert got.right_neighbor is None
