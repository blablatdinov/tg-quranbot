# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Generic, final, override

import attrs
import jsonpath_ng

from app_types.stringable import SupportsStr
from services.json_path import ET_co, JsonPath


@final
@attrs.define(frozen=True)
class JsonPathValue(JsonPath, Generic[ET_co]):
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
    def evaluate(self) -> ET_co:
        """Получить значение.

        :return: T
        :raises ValueError: если поиск не дал результатов
        """
        match = jsonpath_ng.parse(self._json_path).find(self._json)
        if not match:
            raise ValueError
        return match[0].value
