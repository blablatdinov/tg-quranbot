# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Iterable
from contextlib import suppress
from typing import Generic, final, override

import attrs

from app_types.stringable import SupportsStr
from services.json_path import ET_co, JsonPath
from services.json_path_value import JsonPathValue


@final
@attrs.define(frozen=True)
class MatchManyJsonPath(JsonPath, Generic[ET_co]):
    """Поиск по нескольким jsonpath."""

    _json: dict
    _json_paths: Iterable[SupportsStr]

    @override
    def evaluate(self) -> ET_co:
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
