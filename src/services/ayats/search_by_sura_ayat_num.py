from typing import Optional

from exceptions.content_exceptions import AyatNotFoundError, SuraNotFoundError
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from services.ayats.ayat_search import AyatSearchInterface


class AyatBySuraAyatNum(AyatSearchInterface):
    """Класс, обрабатывающий логику поиска аятов."""

    _ayat_repository: AyatRepositoryInterface
    _search_input: str

    def __init__(self, ayat_repository: AyatRepositoryInterface, search_input: str):
        self._search_input = search_input
        self._ayat_repository = ayat_repository

    async def search(self) -> Ayat:
        """Поиск по номеру суры и аята.

        :returns: Ayat
        :raises AyatNotFoundError: if ayat not found
        """
        sura_num, ayat_num = self._search_input.split(':')
        ayats = await self._ayat_repository.get_ayats_by_sura_num(int(sura_num))
        self._validate_sura_ayat_numbers(int(sura_num), int(ayat_num))
        for ayat in ayats:
            result_ayat = self._search_in_sura_ayats(ayat, ayat_num)

            if result_ayat:
                return result_ayat

        raise AyatNotFoundError

    def _search_in_sura_ayats(self, ayat: Ayat, ayat_num: str) -> Optional[Ayat]:
        result_ayat = None
        if '-' in ayat.ayat_num:
            result_ayat = self._service_range_case(ayat, ayat_num)
        elif ',' in ayat.ayat_num:
            result_ayat = self._service_comma_case(ayat, ayat_num)
        elif ayat.ayat_num == ayat_num:
            result_ayat = ayat

        return result_ayat

    def _validate_sura_ayat_numbers(self, sura_num: int, ayat_num: int) -> None:
        max_sura_num = 114
        if not 0 < sura_num <= max_sura_num:  # noqa: WPS508
            # https://github.com/wemake-services/wemake-python-styleguide/issues/1942
            raise SuraNotFoundError
        if ayat_num <= 0:
            raise AyatNotFoundError

    def _service_range_case(self, ayat: Ayat, ayat_num: str) -> Optional[Ayat]:
        left, right = map(int, ayat.ayat_num.split('-'))
        ayats_range = range(left, right + 1)
        if int(ayat_num) in ayats_range:
            return ayat
        return None

    def _service_comma_case(self, ayat: Ayat, ayat_num: str) -> Optional[Ayat]:
        left, right = map(int, ayat.ayat_num.split(','))
        ayats_range = range(left, right + 1)
        if int(ayat_num) in ayats_range:
            return ayat
        return None


class AyatSearchWithNeighbors(AyatSearchInterface):
    """Поиск аятов по номеру суры и аята с соседними аятами."""

    _ayat_search: AyatSearchInterface
    _neighbor_ayats_repository: NeighborAyatsRepositoryInterface

    def __init__(
        self,
        ayat_by_sura_num: AyatSearchInterface,
        neighbor_ayats_repository: NeighborAyatsRepositoryInterface,
    ):
        self._ayat_search = ayat_by_sura_num
        self._neighbor_ayats_repository = neighbor_ayats_repository

    async def search(self) -> Ayat:
        """Поиск.

        :returns: Ayat
        """
        ayat = await self._ayat_search.search()
        neighbors = await self._neighbor_ayats_repository.get_ayat_neighbors(ayat.id)
        if len(neighbors) == 2 and neighbors[0].id == ayat.id:
            ayat.right_neighbor = neighbors[1]
            return ayat
        elif len(neighbors) == 2 and neighbors[0].id != ayat.id:
            ayat.left_neighbor = neighbors[0]
            return ayat
        elif len(neighbors) == 1:
            return ayat
        ayat.left_neighbor = neighbors[0]
        ayat.right_neighbor = neighbors[2]
        return ayat
