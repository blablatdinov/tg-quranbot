from typing import final, override

from srv.ayats.text_search_query import TextSearchQuery


@final
class CachedTextSearchQuery(TextSearchQuery):
    """Закэшированный запрос."""

    @override
    def __init__(self, origin: TextSearchQuery) -> None:
        """Ctor.

        :param origin: TextSearchQuery
        """
        self._origin = origin
        self._cached = ''

    @override
    async def write(self, query: str) -> None:
        """Запись.

        :param query: str
        """
        await self._origin.write(query)
        self._cached = query

    @override
    async def read(self) -> str:
        """Чтение.

        :return: str
        """
        if self._cached:
            return self._cached
        self._cached = await self._origin.read()
        return self._cached
