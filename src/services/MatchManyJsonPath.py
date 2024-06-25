from app_types.stringable import SupportsStr
from services.JsonPathValue import JsonPathValue
from services.json_path import JsonPath


import attrs
from pyeo import elegant


from collections.abc import Iterable
from contextlib import suppress
from typing import Generic, final, override


@final
@attrs.define(frozen=True)
@elegant
class MatchManyJsonPath(JsonPath, Generic[_ET_co]):
    """Поиск по нескольким jsonpath."""

    _json: dict
    _json_paths: Iterable[SupportsStr]

    @override
    def evaluate(self) -> _ET_co:
        """Получить значение.

        :return: T
        :raises ValueError: если поиск не дал результатов
        """
        for path in self._json_paths:
            with suppress(ValueError):
                return JsonPathValue(
                    self._json,
                    path,
                ).evaluate()
        raise ValueError