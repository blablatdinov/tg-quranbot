from typing import final, override

import attrs
import ujson
from pyeo import elegant

from app_types.stringable import SupportsStr
from app_types.update import Update


@final
@attrs.define(frozen=True)
@elegant
class FkUpdate(Update):
    """Подделка обновления."""

    _raw: SupportsStr | None = '{}'  # noqa: P103. Empty json

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        return str(self._raw)

    @override
    def asdict(self) -> dict:
        """Словарь.

        :return: dict
        """
        return ujson.loads(str(self._raw))
