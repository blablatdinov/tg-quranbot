from typing import Union

from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.schemas import Ayat
from repository.ayats.sura import SuraInterface
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.search.ayat_search_query import SearchQuery, ValidatedSearchQuery


class AyatBySuraAyatNum(AyatSearchInterface):
    """Поиск аята по номеру суры, аята."""

    def __init__(self, sura: SuraInterface):
        self._sura = sura

    async def search(self, search_query: Union[str, int]) -> Ayat:
        """Поиск аята.

        :param search_query: Union[str, int]
        :return: list[httpx.Request]
        :raises AyatNotFoundError: if ayat not found
        :raises TypeError: if search query has int type
        """
        if isinstance(search_query, int):
            raise TypeError
        query = ValidatedSearchQuery(
            SearchQuery(search_query),
        )
        ayat_num = query.ayat()
        ayats = await self._sura.ayats(query.sura())
        for ayat in ayats:
            result_ayat = self._search_in_sura_ayats(ayat, ayat_num)
            if result_ayat:
                return result_ayat[0]
        raise AyatNotFoundError

    def _search_in_sura_ayats(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        result_ayat: tuple[Ayat, ...] = ()
        if '-' in ayat.ayat_num:
            result_ayat = self._service_range_case(ayat, ayat_num)
        elif ',' in ayat.ayat_num:
            result_ayat = self._service_comma_case(ayat, ayat_num)
        elif ayat.ayat_num == ayat_num:
            result_ayat = (ayat,)
        return result_ayat

    def _service_range_case(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        left, right = map(int, ayat.ayat_num.split('-'))
        if int(ayat_num) in range(left, right + 1):
            return (ayat,)
        return ()

    def _service_comma_case(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        left, right = map(int, ayat.ayat_num.split(','))
        if int(ayat_num) in range(left, right + 1):
            return (ayat,)
        return ()
