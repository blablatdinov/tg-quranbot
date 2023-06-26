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
import re
from typing import final

import attrs

from app_types.stringable import Stringable
from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError


@final
@attrs.define(frozen=True)
class MessageText(Stringable):
    """Текст сообщения."""

    _update: Update

    def __str__(self):
        """Строковое представление.

        :return: str
        :raises MessageTextNotFoundError: если текст сообщения не найден
        """
        regex_res = re.search('text"(:|: )"(.+?)"', str(self._update))
        if not regex_res:
            raise MessageTextNotFoundError
        return regex_res.group(2)
