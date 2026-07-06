# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from contextlib import suppress
from typing import Generic, final, override

import attrs

from services.json_path import ET_co, JsonPath


@final
@attrs.define(frozen=True)
class ErrRedirectJsonPath(JsonPath, Generic[ET_co]):
    """JsonPath с преобразованием исключений."""

    _origin: JsonPath
    _to_error: Exception

    @override
    def evaluate(self) -> ET_co:
        """Получить значение.

        :return: T
        :raises _to_error: преобразуемое исключение
        """
        with suppress(ValueError):
            return self._origin.evaluate()
        raise self._to_error
