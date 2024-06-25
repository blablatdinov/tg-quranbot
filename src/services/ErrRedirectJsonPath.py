from contextlib import suppress
from typing import Generic, final, override

import attrs
from pyeo import elegant

from services.json_path import JsonPath


@final
@attrs.define(frozen=True)
@elegant
class ErrRedirectJsonPath(JsonPath, Generic[_ET_co]):
    """JsonPath с преобразованием исключений."""

    _origin: JsonPath
    _to_error: Exception

    @override
    def evaluate(self) -> _ET_co:
        """Получить значение.

        :return: T
        :raises _to_error: преобразуемое исключение
        """
        with suppress(ValueError):
            return self._origin.evaluate()
        raise self._to_error
