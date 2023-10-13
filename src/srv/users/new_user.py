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
from typing import Protocol, final, override

import attrs
from asyncpg import ForeignKeyViolationError, UniqueViolationError
from databases import Database
from loguru import logger
from pyeo import elegant

from exceptions.internal_exceptions import UserNotFoundError
from exceptions.user import UserAlreadyExistsError
from integrations.tg.chat_id import TgChatId
from services.start.start_message import AsyncIntOrNone, FkAsyncIntOrNone


@elegant
class NewUser(Protocol):
    """Новый пользователь."""

    async def create(self) -> None:
        """Создание."""


@final
@attrs.define(frozen=True)
@elegant
class FkNewUser(NewUser):
    """Фейк нового пользователя."""

    @override
    async def create(self) -> None:
        """Создание."""


@final
@attrs.define(frozen=True)
@elegant
class PgNewUser(NewUser):
    """Новый пользователь в БД postgres."""

    _referrer_chat_id: AsyncIntOrNone
    _new_user_chat_id: TgChatId
    _pgsql: Database

    @classmethod
    def ctor(cls, new_user_chat_id: TgChatId, pgsql: Database) -> NewUser:
        """Конструктор без реферера.

        :param new_user_chat_id: TgChatId
        :param pgsql: Database
        :return: NewUser
        """
        return cls(
            FkAsyncIntOrNone(None),
            new_user_chat_id,
            pgsql,
        )

    @override
    async def create(self) -> None:
        """Создание.

        :raises UserAlreadyExistsError: пользователь уже зарегистрирован
        :raises UserNotFoundError: не найден реферер
        """
        chat_id = int(self._new_user_chat_id)
        logger.debug('Insert in DB User <{0}>...'.format(chat_id))
        query = """
            INSERT INTO
            users (chat_id, referrer_id, day)
            VALUES (:chat_id, :referrer_id, 2)
            RETURNING (chat_id, referrer_id)
        """
        try:
            await self._pgsql.fetch_one(
                query,
                {'chat_id': chat_id, 'referrer_id': await self._referrer_chat_id.to_int()},
            )
        except UniqueViolationError as err:
            raise UserAlreadyExistsError from err
        except ForeignKeyViolationError as err:
            raise UserNotFoundError from err
        logger.debug('User <{0}> inserted in DB'.format(chat_id))
