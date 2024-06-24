from typing import final, override

import attrs
from pyeo import elegant

from srv.ayats.text_search_query import TextSearchQuery


@final
@attrs.define(frozen=True)
@elegant
class FkTextSearchQuery(TextSearchQuery):
    """Фейковый запрос для поиска аятов."""

    _query: str

    @override
    async def write(self, query: str) -> None:
        """Запись.

        :param query: str
        """

    @override
    async def read(self) -> str:
        """Чтение.

        :return: str
        """
        return self._query
