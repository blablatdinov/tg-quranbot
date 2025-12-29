# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import re
from typing import SupportsInt, final, override

import attrs

from app_types.stringable import SupportsStr
from exceptions.base_exception import BaseAppError


@final
@attrs.define(frozen=True)
class IntableRegex(SupportsInt):
    """Регулярное выражение, которое можно привести к числу."""

    _text_for_searching: SupportsStr

    @override
    def __int__(self) -> int:
        """Приведение к числу.

        :returns: int
        :raises BaseAppError: если не удалось получить результат по регулярному выражению
        """
        regex_result = re.search(r'\d+', str(self._text_for_searching))
        if not regex_result:
            raise BaseAppError
        finded = regex_result.group(0)
        return int(finded)
