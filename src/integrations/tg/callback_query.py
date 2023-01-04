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
import json

from app_types.stringable import Stringable
from integrations.tg.exceptions.update_parse_exceptions import CallbackQueryNotFoundError


class CallbackQueryData(Stringable):
    """Информация с кнопки."""

    def __init__(self, raw: Stringable):
        """Конструктор класса.

        :param raw: Stringable
        """
        self._raw = raw

    def __str__(self):
        """Строковое представление.

        :return: str
        :raises CallbackQueryNotFoundError: если не удалось получить данные с кнопки
        """
        parsed_json = json.loads(str(self._raw))
        try:
            return parsed_json['callback_query']['data']
        except KeyError as err:
            raise CallbackQueryNotFoundError from err
