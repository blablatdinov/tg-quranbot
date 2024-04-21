"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
from typing import Protocol, SupportsInt, final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.intable import AsyncIntable, FkAsyncIntable
from exceptions.internal_exceptions import UserNotFoundError


@elegant
class User(Protocol):
    """Интерфейс пользователя."""

    async def chat_id(self) -> int:
        """Идентификатор чата."""

    async def day(self) -> int:
        """День для рассылки утреннего контента."""

    async def is_active(self) -> bool:
        """Статус активности пользователя."""


@elegant
class ValidChatId(AsyncIntable, Protocol):
    """Проверенный идентификатор чата."""

    async def to_int(self) -> int:
        """Числовое представление."""


@final
@attrs.define(frozen=True)
@elegant
class FkValidChatId(ValidChatId):
    """Фейковый объект с валидным идентификатором чата.

    Использовать для случаев создания пользователя если мы уверены в наличии идентификатора в хранилище.
    Например: srv.users.active_users.ActiveUsers
    """

    _origin: AsyncIntable

    @classmethod
    def int_ctor(cls, int_value: SupportsInt) -> ValidChatId:
        """Числовой конструктор.

        :param int_value: SupportsInt
        :return: FkValidChatId
        """
        return cls(FkAsyncIntable(int_value))

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        :raises UserNotFoundError: если пользователь не найден
        """
        return await self._origin.to_int()


@final
@attrs.define(frozen=True)
@elegant
class PgValidChatId(ValidChatId):
    """Проверенный идентификатор чата в БД postgres."""

    _pgsql: Database
    _unreliable: AsyncIntable

    @classmethod
    def int_ctor(cls, pgsql: Database, int_value: SupportsInt) -> ValidChatId:
        """Числовой конструктор.

        :param pgsql: Database
        :param int_value: SupportsInt
        :return: FkValidChatId
        """
        return cls(pgsql, FkAsyncIntable(int_value))

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        :raises UserNotFoundError: если пользователь не найден
        """
        chat_id = await self._pgsql.fetch_val(
            '\n'.join([
                'SELECT chat_id',
                'FROM users',
                'WHERE chat_id = :chat_id',
            ]),
            {'chat_id': await self._unreliable.to_int()},
        )
        if not chat_id:
            raise UserNotFoundError
        return chat_id


@final
@attrs.define(frozen=True)
@elegant
class FkUser(User):
    """Фейковый пользователь."""

    _chat_id: int
    _day: int
    _is_active: bool

    @override
    async def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        """
        return self._chat_id

    @override
    async def day(self) -> int:
        """День для рассылки утреннего контента.

        :return: int
        """
        return self._day

    @override
    async def is_active(self) -> bool:
        """Статус пользователя.

        :return: bool
        """
        return self._is_active


@final
@attrs.define(frozen=True)
@elegant
class ChatIdByLegacyId(AsyncIntable):
    """Идентификатор чата по старому идентификатору в БД.

    Остались реферальные ссылки, сгенерированные на предыдущей версии бота
    """

    _pgsql: Database
    _legacy_id: AsyncIntable

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        """
        query = '\n'.join([
            'SELECT chat_id',
            'FROM users',
            'WHERE legacy_id = :legacy_id',
        ])
        return await self._pgsql.fetch_val(query, {'legacy_id': await self._legacy_id.to_int()})


@final
@attrs.define(frozen=True)
@elegant
class PgUser(User):
    """Пользователь в БД postgres."""

    _chat_id: ValidChatId
    _pgsql: Database

    @classmethod
    def legacy_id_ctor(cls, legacy_id: AsyncIntable, pgsql: Database) -> User:
        """Конструктор по старому идентификатору в БД.

        :param legacy_id: int
        :param pgsql: Database
        :return: User
        """
        return cls(PgValidChatId(pgsql, ChatIdByLegacyId(pgsql, legacy_id)), pgsql)

    @classmethod
    def int_ctor(cls, chat_id: int, pgsql: Database) -> User:
        """Конструктор по идентификатору чата.

        :param chat_id: int
        :param pgsql: Database
        :return: User
        """
        return cls(PgValidChatId(pgsql, FkAsyncIntable(chat_id)), pgsql)

    @override
    async def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        """
        return await self._chat_id.to_int()

    @override
    async def day(self) -> int:
        """День для рассылки утреннего контента.

        :return: int
        """
        query = '\n'.join([
            'SELECT day',
            'FROM users',
            'WHERE chat_id = :chat_id',
        ])
        return await self._pgsql.fetch_val(query, {'chat_id': await self._chat_id.to_int()})

    @override
    async def is_active(self) -> bool:
        """Статус пользователя.

        :return: bool
        """
        query = '\n'.join([
            'SELECT is_active',
            'FROM users',
            'WHERE chat_id = :chat_id',
        ])
        return await self._pgsql.fetch_val(query, {'chat_id': await self._chat_id.to_int()})
