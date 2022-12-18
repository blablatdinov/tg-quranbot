from typing import Protocol, Union

from repository.ayats.schemas import Ayat


class AyatSearchInterface(Protocol):
    """Интерфейс поиска аята."""

    async def search(self, search_query: Union[str, int]) -> Ayat:
        """Поиск аята.

        :param search_query: str
        """
