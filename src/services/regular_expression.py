"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from pyeo import elegant
import re
from typing import final

import attrs

from app_types.intable import Intable
from exceptions.base_exception import BaseAppError


@final
@attrs.define(frozen=True)
@elegant
class IntableRegularExpression(Intable):
    """Регулярное выражение, которое можно привести к числу."""

    _text_for_searching: str

    def __int__(self) -> int:
        """Приведение к числу.

        :returns: int
        :raises BaseAppError: если не удалось получить результат по регулярному выражению
        """
        regex_result = re.search(r'\d+', self._text_for_searching)
        if not regex_result:
            raise BaseAppError
        finded = regex_result.group(0)
        return int(finded)
