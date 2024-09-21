# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import final, override

import attrs
from asyncpg import ForeignKeyViolationError, UniqueViolationError
from databases import Database

from app_types.async_int_or_none import AsyncIntOrNone
from app_types.fk_async_int_or_none import FkAsyncIntOrNone
from app_types.logger import LogSink
from exceptions.internal_exceptions import UserNotFoundError
from exceptions.user import UserAlreadyExistsError
from integrations.tg.fk_chat_id import ChatId
from srv.users.new_user import NewUser


@final
@attrs.define(frozen=True)
class PgNewUser(NewUser):
    """Новый пользователь в БД postgres."""

    _referrer_chat_id: AsyncIntOrNone
    _new_user_chat_id: ChatId
    _pgsql: Database
    _logger: LogSink

    @classmethod
    def ctor(cls, new_user_chat_id: ChatId, pgsql: Database, logger: LogSink) -> NewUser:
        """Конструктор без реферера.

        :param new_user_chat_id: ChatId
        :param pgsql: Database
        :param logger: LogSink
        :return: NewUser
        """
        return cls(
            FkAsyncIntOrNone(None),
            new_user_chat_id,
            pgsql,
            logger,
        )

    @override
    async def create(self) -> None:
        """Создание.

        :raises UserAlreadyExistsError: пользователь уже зарегистрирован
        :raises UserNotFoundError: не найден реферер
        """
        chat_id = int(self._new_user_chat_id)
        self._logger.debug('Insert in DB User <{0}>...'.format(chat_id))
        query = '\n'.join([
            'INSERT INTO',
            'users (chat_id, referrer_id, day, is_active)',
            'VALUES (:chat_id, :referrer_id, 2, true)',
            'RETURNING (chat_id, referrer_id)',
        ])
        try:
            await self._pgsql.fetch_one(
                query,
                {'chat_id': chat_id, 'referrer_id': await self._referrer_chat_id.to_int()},
            )
        except UniqueViolationError as err:
            raise UserAlreadyExistsError from err
        except ForeignKeyViolationError as err:
            raise UserNotFoundError from err
        self._logger.debug('User <{0}> inserted in DB'.format(chat_id))
