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

from app_types.intable import Intable
from app_types.stringable import Stringable, UnwrappedString
from integrations.tg.exceptions.update_parse_exceptions import InlineQueryIdNotFoundError, InlineQueryNotFoundError


class InlineQuery(Stringable):
    """Данные с инлайн поиска."""

    def __init__(self, update: Stringable):
        """Конструктор класса.

        :param update: Stringable
        """
        self._update = update

    def __str__(self):
        """Строковое представление.

        :return: str
        :raises InlineQueryNotFoundError: если не найдены данные инлайн поиска
        """
        unwrapped_string = str(self._update)
        query_regex_result = re.search('query"(:|: )"(.+?)"', unwrapped_string)
        if not query_regex_result:
            raise InlineQueryNotFoundError
        return query_regex_result.group(2)


class InlineQueryId(Intable):
    """Идентификатор инлайн поиска."""

    def __init__(self, update: Stringable):
        """Конструктор класса.

        :param update: Stringable
        """
        self._update = update

    def __int__(self):
        """Числовое представление.

        :return: int
        :raises InlineQueryIdNotFoundError: если не найден идентификатор инлайн поиска
        """
        unwrapped_string = str(UnwrappedString(self._update))
        regex_result = re.search('inline_query"(:|: )({.+?})', unwrapped_string)
        if not regex_result:
            raise InlineQueryIdNotFoundError
        regex_result = re.search(r'id"(:|: )"(\d+)"', regex_result.group(2))
        if not regex_result:
            raise InlineQueryIdNotFoundError
        return int(regex_result.group(2))
