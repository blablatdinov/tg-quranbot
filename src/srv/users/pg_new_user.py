# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
