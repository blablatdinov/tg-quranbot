from typing import Union

from repository.ayats.ayat import AyatRepositoryInterface
from repository.ayats.schemas import Ayat
from services.ayats.search_by_sura_ayat_num import AyatSearchInterface


class AyatById(AyatSearchInterface):
    """Поиск аята по идентификатору аята."""

    def __init__(self, ayat_repo: AyatRepositoryInterface):
        """Конструктор класса.

        :param ayat_repo: AyatRepositoryInterface
        """
        self._ayat_repo = ayat_repo

    async def search(self, search_query: Union[str, int]) -> Ayat:
        """Поиск аята.

        :param search_query: str
        :return: list[httpx.Request]
        :raises TypeError: if search has str type
        """
        if isinstance(search_query, str):
            raise TypeError
        return await self._ayat_repo.get(search_query)
