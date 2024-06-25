from typing import final, override

import attrs
from pyeo import elegant

from app_types.AsyncSupportsStr import AsyncSupportsStr


@final
@attrs.define(frozen=True)
@elegant
class FkAsyncStr(AsyncSupportsStr):
    """Обертка для строки."""

    _source: str

    @override
    async def to_str(self) -> str:
        """Строковое представление.

        :return: str
        """
        return self._source
