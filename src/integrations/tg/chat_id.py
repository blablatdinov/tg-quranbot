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
from exceptions.base_exception import InternalBotError


class TgChatId(Intable):
    """Идентификатор чата."""

    def __init__(self, update: Stringable):
        """Конструктор класса.

        :param update: Stringable
        """
        self._update = update

    def __int__(self):
        """Числовое представление.

        :return: int
        :raises InternalBotError: В случае отсутсвия идентификатора чата в json
        """
        unwrapped_string = str(UnwrappedString(self._update))
        chat_json_object = re.search('chat"(:|: )({.+?})', unwrapped_string)
        if chat_json_object:
            return self._parse_id(chat_json_object)
        chat_json_object = re.search('from"(:|: )({.+?})', unwrapped_string)
        if chat_json_object:
            return self._parse_id(chat_json_object)
        raise InternalBotError

    def _parse_id(self, chat_json_object: re.Match) -> int:
        chat_id_regex_result = re.search(r'id"(:|: )(\d+)', chat_json_object.group(2))
        if not chat_id_regex_result:
            raise InternalBotError
        return int(chat_id_regex_result.group(2))
