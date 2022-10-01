from typing import Union

from repository.ayats.schemas import Ayat


class AyatSearchInterface(object):
    """Интерфейс поиска аята."""

    async def search(self, search_query: Union[str, int]) -> Ayat:
        """Поиск аята.

        :param search_query: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
