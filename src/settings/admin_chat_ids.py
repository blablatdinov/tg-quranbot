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
from collections.abc import Sequence
from typing import final, overload

import attrs

from settings.settings import Settings


@final
@attrs.define(frozen=True)
class AdminChatIds(Sequence[int]):
    """Список идентификаторов администраторов."""

    _settings: Settings

    @overload
    def __getitem__(self, idx: int) -> int:
        """Тип для индекса.

        :param idx: int
        """

    @overload
    def __getitem__(self, idx: slice) -> Sequence[int]:
        """Тип для среза.

        :param idx: slice
        """

    def __getitem__(self, idx: int | slice) -> int | Sequence[int]:
        """Получить элемент.

        :param idx: int
        :return: int
        """
        return [
            int(chat_id.strip()) for chat_id in self._settings.ADMIN_CHAT_IDS.split(',')
        ][idx]

    def __len__(self) -> int:
        """Кол-во администраторов.

        :return: int
        """
        return len(self._settings.ADMIN_CHAT_IDS.split(','))

    def count(self, search_value: int) -> int:
        """Кол-во элементов.

        :param search_value: int
        :return: int
        """
        return [
            int(chat_id.strip()) for chat_id in self._settings.ADMIN_CHAT_IDS.split(',')
        ].count(search_value)
