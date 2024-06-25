from app_types.stringable import SupportsStr
from services.json_path import JsonPath


import attrs
import jsonpath_ng
from pyeo import elegant


from typing import Generic, final, override


@final
@attrs.define(frozen=True)
@elegant
class JsonPathValue(JsonPath, Generic[_ET_co]):
    """Объект, получающий значение по jsonpath.

    Пример поиска идентификатора чата:

    .. code-block:: python3

        int(
            SafeJsonPathValue(
                MatchManyJsonPath(
                    self._update.asdict(),
                    ('$..chat.id', '$..from.id'),
                ),
                InternalBotError(),
            ).evaluate(),
        )
    """

    _json: dict
    _json_path: SupportsStr

    @override
    def evaluate(self) -> _ET_co:
        """Получить значение.

        :return: T
        :raises ValueError: если поиск не дал результатов
        """
        match = jsonpath_ng.parse(self._json_path).find(self._json)
        if not match:
            raise ValueError
        return match[0].value