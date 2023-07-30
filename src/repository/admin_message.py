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
from typing import Protocol, final

import attrs
from databases import Database
from pyeo import elegant

from exceptions.base_exception import InternalBotError


@elegant
class AdminMessageInterface(Protocol):
    """Интерфейс административного сообщения."""

    async def text(self) -> str:
        """Чтение содержимого административного сообщения."""


@final
@attrs.define(frozen=True)
@elegant
class AdminMessage(AdminMessageInterface):
    """Административное сообщение."""

    _key: str
    _connection: Database

    async def text(self) -> str:
        """Текст административного сообщения.

        :raises InternalBotError: возбуждается если административное сообщение с переданным ключом не найдено
        :return: str
        """
        record = await self._connection.fetch_one(
            'SELECT text FROM admin_messages m WHERE m.key = :key', {'key': self._key},
        )
        if not record:
            raise InternalBotError('Не найдено административное сообщение с ключом {0}'.format(self._key))
        return record._mapping['text']  # noqa: WPS437
